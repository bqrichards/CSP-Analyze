function openDrawerMenu(){
	var x = document.getElementById("main-navbar");
	if (x.className === "navbar"){
		x.className += " responsive";
	} else {
		x.className = "navbar";
	}
}