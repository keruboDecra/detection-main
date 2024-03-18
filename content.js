chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  return false;
});

document.addEventListener("DOMContentLoaded", () => {
  console.log("Content script loaded");
  const pageText = document.body.innerText.trim();
  chrome.runtime.sendMessage({ action: "sendTextToAPI", text: pageText });
});

function getText() {
  return document.body.innerText;
}
function getHTML() {
  return document.body.outerHTML;
}
function getURL() {
  return window.location.href;
}

// send url, text, and html to background.js
chrome.runtime.sendMessage({
  action: "sendTextToAPI",
  text: getText(),
  html: getHTML(),
  url: getURL(),
});
