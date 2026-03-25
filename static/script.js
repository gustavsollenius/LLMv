
baseURL = window.location.href;

async function handleButton(){
    
    var responseURL = "response"
    var data = "default";

    try{
        const response = await fetch(baseURL + responseURL);
        data = await response.json();

    }catch(err){
        console.error(err);
    }


    var textBox = document.getElementsByClassName("center-text-box")[0]

    var p = document.createElement("p");
    p.innerText = data.message;
    textBox.appendChild(p);
}