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