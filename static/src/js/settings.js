/**
 * to change btn text when htmx request sent
 */
function ch_btn_text(elId) {
    let button = document.getElementById(elId);
    if (button) {
        let originalText = button.innerText;
        let newText = event.detail.xhr.responseText;
        button.innerText = newText;

        if (button.innerText == 'Disabled') {
            if (elId === 'toggle-telegram-btn') {
                clearInput('telegram-input', elId);
            } else if (elId === 'toggle-discord-btn') {
                clearInput('discord-input', elId);
            }
        }
    
        setTimeout(function() {
            button.innerText = (originalText === 'Disabled' ? 'Add' : 'Remove');
        }, 2000);
    }
}

/**
 * to empty input
 */
function clearInput(inId, btn) {
    document.getElementById(inId).value = '';
    document.getElementById(btn).disabled = true;
}

/**
 * to disable btn if input empty
 */
const telegramInput = document.getElementById('telegram-input');
const telegramBtn = document.getElementById('toggle-telegram-btn');
const discordInput = document.getElementById('discord-input');
const discordBtn = document.getElementById('toggle-discord-btn');

function checkInputValue(input, btn) {
    if (input.value.length !== 0) {
        btn.disabled = false;
    } else {
        btn.disabled = true;
    }
}
checkInputValue(telegramInput, telegramBtn);
checkInputValue(discordInput, discordBtn);

telegramInput.addEventListener('input', () => {
    checkInputValue(telegramInput, telegramBtn);
});

discordInput.addEventListener('input', () => {
    checkInputValue(discordInput, discordBtn);
});



