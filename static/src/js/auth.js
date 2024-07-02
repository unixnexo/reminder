function startCounter() {
    const btn = document.getElementById('sbt_btn');
    const verifyText = document.getElementById('verify-text');
    const counterUi = document.querySelector('.countdown');

    let counter = 90
    const interval = setInterval(() => {
        if (counter > 0) {
            counter--
            document.querySelector('.countdown span').style.setProperty('--value', counter)
        }
        if (counter === 0) {
            counterUi.classList.add('hidden');
            verifyText.classList.remove('hidden');
            btn.disabled = false;
            clearInterval(interval); 
        }
    }, 1000)
}

