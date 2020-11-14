'use strict';


let shortenForm = document.getElementById("shorten-form");
shortenForm.addEventListener("submit", shortenUrl);
shortenForm.submit = shortenUrl;

let shortenResult = document.getElementById("shorten-result");
let shortenError = document.getElementById("shorten-error");


function stripHttp(url) {
    if (!url.indexOf("http://www")) {
        url = url.substring(11)
    } else if (!url.indexOf("https://www")) {
        url = url.substring(12)
    } else if (!url.indexOf("https://")) {
        url = url.substring(8)
    } else if (!url.indexOf("http://")) {
        url = url.substring(7)
    }

    return url
}


async function shortenUrl(event) {
    event.preventDefault();
    let url = document.getElementById("url").value;

    let response = await fetch('/shorten', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json;charset=utf-8'
        },
        body: JSON.stringify({
            'url': url
        })
    });
    shortenResult.classList.add('hide');
    shortenError.classList.add('hide');
    if (response.ok) {
        let json = await response.json();
        if (json.error) {
            shortenError.innerHTML = `<p>${json.error}</p>`
            shortenError.classList.remove('hide');
            return;
        }
        let buildUrl = `${window.location.origin}/${json.hash}`;
        let stripUrl = stripHttp(buildUrl);
        shortenResult.innerHTML = `<a href="${buildUrl}" target="_blank">${stripUrl}</a> <span onclick="copyUrl(this);">Copy url</span>`;
        shortenResult.classList.remove('hide');
    } else {
        shortenError.innerHTML = `<p>${response.statusText}</p>`
        shortenError.classList.remove('hide');
        console.log("Ошибка HTTP: " + response.status);
    }
    return false;
}

function copyUrl(elem) {
    let url = document.querySelector("#shorten-result a").innerHTML;
    let textArea = document.createElement("textarea")
    textArea.value = url;
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
    elem.innerHTML = 'Copied';
}