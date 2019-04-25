/**
* Hide a specific team number's item
* @param number the team number to hide
*/
function _hide(number) {
	document.getElementById('team-item-' + number).style.display = 'none';
}

/**
* Show a specific team number's item
* @param number the team number to show
*/
function _show(number) {
	document.getElementById('team-item-' + number).style.display = 'block';
}

/**
* Unhide all team items
*/
function unhideAll() {
	const items = document.getElementsByClassName('grid-item');
	for (var i = 0; i < items.length; i++) {
		items[i].style.display = 'block';
	}
}

/**
* Hide teams that don't contain these numbers
* @param number the number to filter teams by
*/
function filterByNumber(number) {
const items = document.getElementsByClassName('grid-item');
	for (var i = 0; i < items.length; i++) {
		// Check if this team number matches this number
		const teamNumberText = items[i].getElementsByClassName('team-number-span')[0].innerHTML;
		const teamNumber = teamNumberText.split('#')[1];
		const hide = !teamNumber.includes(number);
		items[i].style.display = hide ? 'none' : 'block';
	}
}

// Add listener to search text box
document.getElementById('search-bar').addEventListener('input', function() {
	const search = document.getElementById('search-bar').value;

	if (!search) {
		console.log('No search value, unhide all teams');
		unhideAll();
		return;
	}

	if (isNaN(search)) {
		console.log('Search value is not a number, unhide all');
		unhideAll();
		return;
	}

	filterByNumber(search);
});