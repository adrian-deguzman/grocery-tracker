// --- Globals ---
let currentEditingSelectedState = true;
let currentEditingImage = null; 
let currentEditingStatus = 'in_cart';
let isTransitioningStatus = false;

window.onload = fetchItems;

// --- Tab Navigation Logic ---
function switchTab(tabName) {
    const viewToBuy = document.getElementById('view-to-buy');
    const viewCart = document.getElementById('view-cart');
    const navToBuy = document.getElementById('nav-to-buy');
    const navCart = document.getElementById('nav-cart');

    if (tabName === 'to-buy') {
        viewToBuy.classList.remove('hidden');
        viewCart.classList.add('hidden');
        navToBuy.classList.replace('text-[#8E8E93]', 'text-[#B3A8FF]');
        navCart.classList.replace('text-[#B3A8FF]', 'text-[#8E8E93]');
    } else if (tabName === 'cart') {
        viewToBuy.classList.add('hidden');
        viewCart.classList.remove('hidden');
        navCart.classList.replace('text-[#8E8E93]', 'text-[#B3A8FF]');
        navToBuy.classList.replace('text-[#B3A8FF]', 'text-[#8E8E93]');
    }
}

// --- Loading UI State ---
function setLoading(isLoading) {
    const spinner = document.getElementById('loading-spinner');
    const totalContainer = document.getElementById('total-container');
    const viewToBuy = document.getElementById('view-to-buy');
    const viewCart = document.getElementById('view-cart');
    
    if (isLoading) {
        spinner.classList.remove('hidden');
        totalContainer.classList.add('opacity-50');
        viewToBuy.classList.add('opacity-50', 'pointer-events-none', 'transition-opacity');
        viewCart.classList.add('opacity-50', 'pointer-events-none', 'transition-opacity');
    } else {
        spinner.classList.add('hidden');
        totalContainer.classList.remove('opacity-50');
        viewToBuy.classList.remove('opacity-50', 'pointer-events-none');
        viewCart.classList.remove('opacity-50', 'pointer-events-none');
    }
}

// --- API Calls ---
async function fetchItems() {
    setLoading(true);
    try {
        const response = await fetch('/api/cart');
        const items = await response.json();
        renderList(items);
    } finally {
        setLoading(false);
    }
}

// Quick Add Bar (Triggered by pressing Enter)
async function handleQuickAdd(event) {
    if (event.key === 'Enter') {
        const input = document.getElementById('quickAddInput');
        const name = input.value.trim();
        if (!name) return;

        setLoading(true);
        try {
            // Defaults to planned with null price/image
            const payload = { name, price: null, qty: 1, image: null, selected: true, status: 'planned' };
            await fetch('/api/cart', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            input.value = '';
            await fetchItems();
        } catch (error) {
            console.error(error);
            setLoading(false);
        }
    }
}

// Add Unplanned Item (Triggered by FAB)
async function addItem() {
    const name = document.getElementById('itemName').value;
    const price = parseFloat(document.getElementById('itemPrice').value) || 0;
    const qty = parseInt(document.getElementById('itemQty').value) || 1;
    const imageFile = document.getElementById('itemImage').files[0];

    if (!name) return alert("Need a name!");

    setLoading(true);
    try {
        let imageB64 = null;
        if (imageFile) {
            imageB64 = await toBase64(imageFile);
        }

        // Unplanned items go straight to the cart
        const payload = { name, price, qty, image: imageB64, selected: true, status: 'in_cart' };

        await fetch('/api/cart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        closeAddModal();
        await fetchItems();
    } catch (error) {
        console.error(error);
        setLoading(false);
    }
}

async function toggleItem(id, itemDataStr) {
    setLoading(true);
    try {
        const itemData = JSON.parse(decodeURIComponent(itemDataStr));
        itemData.selected = !itemData.selected;
        await fetch(`/api/cart/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(itemData)
        });
        await fetchItems();
    } catch (error) {
        console.error(error);
        setLoading(false);
    }
}

async function deleteItem(id) {
    setTimeout(async () => {
        setLoading(true);
        try {
            await fetch(`/api/cart/${id}`, { method: 'DELETE' });
            await fetchItems();
        } catch (error) {
            console.error(error);
            setLoading(false);
        }
    }, 100);
}

// --- Modals Logic ---

// ADD Modal
function openAddModal() {
    document.getElementById('itemName').value = '';
    document.getElementById('itemPrice').value = '';
    document.getElementById('itemQty').value = '1';
    document.getElementById('itemImage').value = '';
    
    const modal = document.getElementById('addModal');
    const inner = document.getElementById('addModalInner');
    modal.classList.remove('opacity-0', 'pointer-events-none');
    inner.classList.remove('scale-95');
    inner.classList.add('scale-100');
}

function closeAddModal() {
    const modal = document.getElementById('addModal');
    const inner = document.getElementById('addModalInner');
    modal.classList.add('opacity-0', 'pointer-events-none');
    inner.classList.remove('scale-100');
    inner.classList.add('scale-95');
}

// EDIT / TRANSITION Modal
function openEditModal(itemDataStr, isTransition = false) {
    const item = JSON.parse(decodeURIComponent(itemDataStr));
    
    document.getElementById('editItemId').value = item.id;
    document.getElementById('editItemName').value = item.name;
    document.getElementById('editItemPrice').value = item.price || '';
    document.getElementById('editItemQty').value = item.qty;
    document.getElementById('editItemImage').value = ''; 
    
    currentEditingSelectedState = item.selected;
    currentEditingImage = item.image; 
    currentEditingStatus = item.status;
    isTransitioningStatus = isTransition;
    
    const nameInput = document.getElementById('editItemName');
    const modalTitle = document.getElementById('editModalTitle');
    const saveBtn = document.getElementById('editSaveBtn');

    // Always ensure the name is editable, even when transitioning
    nameInput.readOnly = false;
    nameInput.classList.remove('opacity-50', 'cursor-not-allowed');

    if (isTransition) {
        // Change UI titles for transition state, but keep the input unlocked
        modalTitle.innerText = "Add Details to Cart";
        saveBtn.innerText = "Confirm to Cart";
    } else {
        // Standard edit mode
        modalTitle.innerText = "Edit Item";
        saveBtn.innerText = "Save Changes";
    }
    
    const previewImg = document.getElementById('editImagePreview');
    if (item.image) {
        previewImg.src = item.image;
        previewImg.classList.remove('hidden');
    } else {
        previewImg.src = '';
        previewImg.classList.add('hidden');
    }
    
    const modal = document.getElementById('editModal');
    const inner = document.getElementById('editModalInner');
    modal.classList.remove('opacity-0', 'pointer-events-none');
    inner.classList.remove('scale-95');
    inner.classList.add('scale-100');
}

function closeEditModal() {
    const modal = document.getElementById('editModal');
    const inner = document.getElementById('editModalInner');
    modal.classList.add('opacity-0', 'pointer-events-none');
    inner.classList.remove('scale-100');
    inner.classList.add('scale-95');
}

async function saveEdit() {
    const id = document.getElementById('editItemId').value;
    const name = document.getElementById('editItemName').value;
    const price = parseFloat(document.getElementById('editItemPrice').value) || 0;
    const qty = parseInt(document.getElementById('editItemQty').value) || 1;
    const imageFile = document.getElementById('editItemImage').files[0];

    if (!name) return alert("Need a name!");

    setLoading(true);
    try {
        let imageB64 = currentEditingImage; 
        if (imageFile) {
            imageB64 = await toBase64(imageFile); 
        }

        // Standard PUT update
        const payload = { name, price, qty, image: imageB64, selected: currentEditingSelectedState, status: currentEditingStatus };
        await fetch(`/api/cart/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        // If transitioning from Planned to Cart, follow up with the PATCH requirement
        if (isTransitioningStatus) {
            await fetch(`/api/cart/${id}/status`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: 'in_cart' })
            });
        }

        closeEditModal();
        await fetchItems();
    } catch(error) {
        console.error(error);
        setLoading(false);
    }
}

// IMAGE Modal
function openImageModal(imgSrc, itemName) {
    const imgEl = document.getElementById('fullScreenImage');
    imgEl.src = imgSrc;
    const downloadBtn = document.getElementById('downloadImageBtn');
    downloadBtn.href = imgSrc;
    const safeName = itemName.replace(/\s+/g, '_');
    downloadBtn.download = `${safeName}.png`;
    
    const modal = document.getElementById('imageModal');
    modal.classList.remove('opacity-0', 'pointer-events-none');
    imgEl.classList.remove('scale-95');
    imgEl.classList.add('scale-100');
}

function closeImageModal() {
    const modal = document.getElementById('imageModal');
    const imgEl = document.getElementById('fullScreenImage');
    modal.classList.add('opacity-0', 'pointer-events-none');
    imgEl.classList.remove('scale-100');
    imgEl.classList.add('scale-95');
    setTimeout(() => { imgEl.src = ""; }, 300);
}

// --- UI Rendering ---
// --- Bulk Actions ---
async function toggleAllCartItems(targetState) {
    setLoading(true);
    try {
        const response = await fetch('/api/cart');
        const items = await response.json();
        
        const promises = [];
        for (const item of items) {
            if (item.status === 'in_cart' && item.selected !== targetState) {
                item.selected = targetState;
                promises.push(fetch(`/api/cart/${item.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(item)
                }));
            }
        }
        
        await Promise.all(promises); // Fire all update requests concurrently
        await fetchItems();
    } catch (error) {
        console.error(error);
        setLoading(false);
    }
}

// --- UI Rendering ---
function renderList(items) {
    const plannedList = document.getElementById('planned-list');
    const cartList = document.getElementById('incart-list');

    let total = 0;
    let cartCount = 0;
    let selectedCartCount = 0;
    
    let plannedHTML = '<h2 class="text-[1.15rem] font-medium text-white mb-1 px-1">Planned Items</h2>';
    let cartHTML = '';

    items.forEach(item => {
        const itemDataStr = encodeURIComponent(JSON.stringify(item));
        const safeImageName = item.name.replace(/'/g, "\\'");
        const formattedPrice = (item.price || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

        if (item.status === 'planned') {
            plannedHTML += `
                <div class="bg-[#1C1C1E] p-4 rounded-[24px] flex items-center justify-between transition-all hover:bg-[#252528]">
                    <div class="flex-grow cursor-pointer" onclick="openEditModal('${itemDataStr}', false)">
                        <p class="font-semibold text-lg text-white leading-tight tracking-wide">${item.name}</p>
                        <p class="text-[#8E8E93] text-[13px] font-medium mt-1 tracking-wide">Qty: ${item.qty}</p>
                    </div>
                    <button onclick="openEditModal('${itemDataStr}', true)" class="flex-shrink-0 ml-3 bg-[#B3A8FF] text-black text-sm font-semibold px-4 py-2.5 rounded-[14px] active:scale-95 transition-transform shadow-lg z-10">
                        Add to Cart
                    </button>
                </div>
            `;
        } else {
            // In Cart
            cartCount++;
            if (item.selected) {
                selectedCartCount++;
                total += ((item.price || 0) * item.qty);
            }

            cartHTML += `
                <div class="cart-item-row bg-[#1C1C1E] p-4 rounded-[24px] flex items-center gap-4 transition-all hover:bg-[#252528]" data-name="${item.name.toLowerCase().replace(/"/g, '&quot;')}">
                    <div class="flex-shrink-0 flex items-center justify-center z-10">
                        <input type="checkbox" class="w-[22px] h-[22px] accent-[#A7E4C5] rounded-md cursor-pointer border-0 bg-[#2C2C2E]" ${item.selected ? 'checked' : ''} 
                               onchange="toggleItem('${item.id}', '${itemDataStr}')">
                    </div>
                    <div class="flex-grow cursor-pointer" onclick="openEditModal('${itemDataStr}', false)">
                        <p class="font-semibold text-lg text-white leading-tight tracking-wide">${item.name}</p>
                        <p class="text-[#8E8E93] text-[13px] font-medium mt-1 tracking-wide">${item.qty} x ₱${formattedPrice}</p>
                    </div>
                    ${item.image ? `<img src="${item.image}" onclick="openImageModal('${item.image}', '${safeImageName}')" class="w-[50px] h-[50px] object-cover rounded-[14px] bg-[#2C2C2E] cursor-pointer hover:opacity-80 transition-opacity z-10">` : ''}
                    <button onclick='deleteItem("${item.id}")' class="text-[#8E8E93] hover:text-red-400 active:scale-90 transition-all text-xl font-bold pl-2 pr-1 z-10">✕</button>
                </div>
            `;
        }
    });

    // Dynamic header state for Cart
    const allSelected = cartCount > 0 && selectedCartCount === cartCount;
    const headerActionText = allSelected ? "Deselect All" : "Select All";
    const headerActionParam = allSelected ? "false" : "true";

    // --- Capture search state before re-render ---
    const searchInputEl = document.getElementById('cartSearchInput');
    const currentSearchQuery = searchInputEl ? searchInputEl.value : "";
    const searchBarEl = document.getElementById('cartSearchBar');
    const isSearchOpen = searchBarEl && !searchBarEl.classList.contains('hidden');

    cartList.innerHTML = `
        <div class="flex justify-between items-center mb-2 px-1 mt-2">
            <h2 class="text-[1.15rem] font-medium text-white">In Cart</h2>
            <div class="flex items-center gap-4">
                <button onclick="document.getElementById('cartSearchBar').classList.toggle('hidden'); document.getElementById('cartSearchInput').focus();" class="text-[#8E8E93] hover:text-white transition-colors active:scale-95">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
                </button>
                ${cartCount > 0 ? `<button onclick="toggleAllCartItems(${headerActionParam})" class="text-[#A7E4C5] text-sm font-semibold hover:opacity-80 transition-opacity tracking-wide">${headerActionText}</button>` : ''}
            </div>
        </div>
        <div id="cartSearchBar" class="${isSearchOpen ? '' : 'hidden'} w-full mb-3 transition-all">
            <input type="text" id="cartSearchInput" oninput="filterCartItems()" value="${currentSearchQuery.replace(/"/g, '&quot;')}" placeholder="Search items in cart..." class="w-full bg-[#1C1C1E] text-white placeholder-[#8E8E93] px-4 py-2.5 rounded-[16px] focus:outline-none focus:ring-2 focus:ring-[#A7E4C5] text-sm border border-[#2C2C2E] shadow-inner">
        </div>
    ` + cartHTML;
    
    plannedList.innerHTML = plannedHTML;

    // Empty States
    if (plannedList.children.length === 1) plannedList.innerHTML += '<p class="text-[#8E8E93] italic px-2 text-sm mt-2">No planned items yet.</p>';
    if (cartCount === 0) cartList.innerHTML += '<p class="text-[#8E8E93] italic px-2 text-sm mt-2">Your cart is empty.</p>';

    // Re-apply filter immediately if there's an active query
    if (currentSearchQuery) filterCartItems();

    // Update UI Badges & Totals
    document.getElementById('grand-total').innerText = total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    
    const badge = document.getElementById('cart-badge');
    if (cartCount > 0) {
        badge.innerText = cartCount;
        badge.classList.remove('hidden');
    } else {
        badge.classList.add('hidden');
    }
}

const toBase64 = file => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = error => reject(error);
});

// --- Live Local Search Filter ---
function filterCartItems() {
    const query = document.getElementById('cartSearchInput').value.toLowerCase();
    const rows = document.querySelectorAll('.cart-item-row');
    
    rows.forEach(row => {
        if (row.getAttribute('data-name').includes(query)) {
            row.classList.remove('hidden');
            row.classList.add('flex'); // Restore original flex layout
        } else {
            row.classList.add('hidden');
            row.classList.remove('flex');
        }
    });
}