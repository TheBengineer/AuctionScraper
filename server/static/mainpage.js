function reload() {
    location.reload();
}

function scrape_new() {
    fetch('/scrape_new')
    return null;
}


function hide_bus(bus_id) {
    fetch(`/hide/${bus_id}`)
    return null;
}

function update_note(element) {
    const val = element.value;
    console.log(`data for Textarea ${element.dataset.id}:`, val);
    element.classList.add('unsaved');

    // 1. Clear the specific timer stored on THIS element
    clearTimeout(element.timer);

    // 2. Set a new timer and attach it back to the element
    element.timer = setTimeout(() => {
        console.log(`Fetching for Textarea ${element.dataset.id}:`, val);
        element.classList.remove('unsaved');
        fetch(`/note/${element.dataset.id}`, {method: 'POST', body: JSON.stringify({note: val})})
    }, 2000);
}