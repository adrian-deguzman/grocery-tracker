// --- Globals ---
let currentEditingSelectedState = true;
let currentEditingImage = null; // Keeps track of existing image in edit mode

window.onload = fetchItems;

async function fetchItems() {
    const response = await fetch('/api/cart');
    const items = await response.json();
    renderList(items);
}

async function addItem() {
    const name = document.getElementById('itemName').value;
    const price = parseFloat(document.getElementById('itemPrice').value) || 0;
    const qty = parseInt(document.getElementById('itemQty').value) || 1;
    const imageFile = document.getElementById('itemImage').files[0];

    if (!name) return alert("Need a name!");

    let imageB64 = null;
    if (imageFile) {
        imageB64 = await toBase64(imageFile);
    }

    const payload = { name, price, qty, image: imageB64, selected: true };

    await fetch('/api/cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    document.getElementById('itemName').value = '';
    document.getElementById('itemPrice').value = '';
    document.getElementById('itemImage').value = '';
    fetchItems();
}

async function toggleItem(id, itemDataStr) {
    const itemData = JSON.parse(decodeURIComponent(itemDataStr));
    itemData.selected = !itemData.selected;
    await fetch(`/api/cart/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(itemData)
    });
    fetchItems();
}

async function deleteItem(id) {
    // Add slight delay to allow scale animation to play before deleting
    setTimeout(async () => {
        await fetch(`/api/cart/${id}`, { method: 'DELETE' });
        fetchItems();
    }, 100);
}

// --- Edit Modal Logic ---
function openEditModal(itemDataStr) {
    const item = JSON.parse(decodeURIComponent(itemDataStr));
    
    document.getElementById('editItemId').value = item.id;
    document.getElementById('editItemName').value = item.name;
    document.getElementById('editItemPrice').value = item.price;
    document.getElementById('editItemQty').value = item.qty;
    document.getElementById('editItemImage').value = ''; // Reset file input
    
    currentEditingSelectedState = item.selected;
    currentEditingImage = item.image; // Keep existing image in memory
    
    // Show the previous image preview if it exists
    const previewImg = document.getElementById('editImagePreview');
    if (item.image) {
        previewImg.src = item.image;
        previewImg.classList.remove('hidden');
    } else {
        previewImg.src = '';
        previewImg.classList.add('hidden');
    }
    
    document.getElementById('editModal').classList.remove('hidden');
}

function closeEditModal() {
    document.getElementById('editModal').classList.add('hidden');
}

async function saveEdit() {
    const id = document.getElementById('editItemId').value;
    const name = document.getElementById('editItemName').value;
    const price = parseFloat(document.getElementById('editItemPrice').value) || 0;
    const qty = parseInt(document.getElementById('editItemQty').value) || 1;
    const imageFile = document.getElementById('editItemImage').files[0];

    if (!name) return alert("Need a name!");

    let imageB64 = currentEditingImage; // Default to old image
    if (imageFile) {
        imageB64 = await toBase64(imageFile); // Overwrite if new uploaded
    }

    const payload = { name, price, qty, image: imageB64, selected: currentEditingSelectedState };

    await fetch(`/api/cart/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    closeEditModal();
    fetchItems();
}

// --- Image Modal Logic ---
function openImageModal(imgSrc, itemName) {
    document.getElementById('fullScreenImage').src = imgSrc;
    
    const downloadBtn = document.getElementById('downloadImageBtn');
    downloadBtn.href = imgSrc;
    
    // Format name: "Item Name" -> "Item_Name.png"
    const safeName = itemName.replace(/\s+/g, '_');
    downloadBtn.download = `${safeName}.png`;
    
    document.getElementById('imageModal').classList.remove('hidden');
}

function closeImageModal() {
    document.getElementById('imageModal').classList.add('hidden');
    document.getElementById('fullScreenImage').src = "";
}

// --- UI Rendering ---
function renderList(items) {
    const listDiv = document.getElementById('cart-list');
    listDiv.innerHTML = '';
    let total = 0;

    if (items.length === 0) {
        listDiv.innerHTML = '<p class="text-[#8E8E93] italic px-2">Your list is currently empty.</p>';
    }

    items.forEach(item => {
        if (item.selected) {
            total += (item.price * item.qty);
        }

        const formattedPrice = item.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        
        // Encode object so we can pass it securely inside HTML strings
        const itemDataStr = encodeURIComponent(JSON.stringify(item));
        const safeImageName = item.name.replace(/'/g, "\\'");

        const itemHTML = `
            <div class="bg-[#1C1C1E] p-4 rounded-[24px] flex items-center gap-4 transition-all hover:bg-[#252528]">
                
                <div class="flex-shrink-0 flex items-center justify-center z-10">
                    <input type="checkbox" class="w-[22px] h-[22px] accent-[#A7E4C5] rounded-md cursor-pointer border-0 bg-[#2C2C2E]" ${item.selected ? 'checked' : ''} 
                           onchange="toggleItem('${item.id}', '${itemDataStr}')">
                </div>
                
                <div class="flex-grow cursor-pointer" onclick="openEditModal('${itemDataStr}')">
                    <p class="font-semibold text-lg text-white leading-tight tracking-wide">${item.name}</p>
                    <p class="text-[#8E8E93] text-[13px] font-medium mt-1 tracking-wide">${item.qty} x ₱${formattedPrice}</p>
                </div>
                
                ${item.image ? `<img src="${item.image}" onclick="openImageModal('${item.image}', '${safeImageName}')" class="w-[50px] h-[50px] object-cover rounded-[14px] bg-[#2C2C2E] cursor-pointer hover:opacity-80 transition-opacity z-10">` : ''}
                
                <button onclick='deleteItem("${item.id}")' class="text-[#8E8E93] hover:text-red-400 active:scale-90 transition-all text-xl font-bold pl-2 pr-1 z-10">✕</button>
            </div>
        `;
        listDiv.innerHTML += itemHTML;
    });

    document.getElementById('grand-total').innerText = total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

const toBase64 = file => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = error => reject(error);
});