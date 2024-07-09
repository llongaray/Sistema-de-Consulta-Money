document.addEventListener('DOMContentLoaded', function () {
    var tabs = document.querySelectorAll('.tabs .tab');
    var tabContents = document.querySelectorAll('.content');
    var tabSliders = document.querySelectorAll('.tab-slider');

    tabs.forEach(function (tab) {
        tab.addEventListener('click', function () {
            var tabGroup = tab.parentNode;
            var tabGroupContents = tabGroup.nextElementSibling.querySelectorAll('.content');

            // Remover classe 'active' de todas as abas e conteúdos
            tabGroup.querySelectorAll('.tab').forEach(function (tab) {
                tab.classList.remove('active');
            });
            tabGroupContents.forEach(function (content) {
                content.classList.remove('active');
            });

            // Adicionar classe 'active' à aba e ao conteúdo correspondente
            tab.classList.add('active');
            document.getElementById(tab.dataset.tab).classList.add('active');

            // Atualizar a posição do slider
            tabSliders.forEach(function (slider) {
                var tabIndex = Array.from(tabGroup.children).indexOf(tab);
                slider.style.left = (tabIndex * 100) + '%';
            });
        });
    });

    // Posição inicial do slider
    const initialActiveTab = document.querySelector('.tabs .tab.active');
    if (initialActiveTab) {
        const tabSlider = document.querySelector('.tab-slider');
        tabSlider.style.left = `${initialActiveTab.offsetLeft}px`;
        tabSlider.style.width = `${initialActiveTab.offsetWidth}px`;
    }
});

// Funções adicionais
function calcularMargem(margemId, coeficienteId, valorLiberadoId) {
    var margem = parseFloat(document.getElementById(margemId).value);
    var coeficiente = parseFloat(document.getElementById(coeficienteId).value);
    if (!isNaN(margem) && !isNaN(coeficiente)) {
        var valorLiberado = margem * (coeficiente / 100);
        document.getElementById(valorLiberadoId).value = 'R$ ' + valorLiberado.toFixed(2);
    } else {
        alert('Por favor, preencha os campos corretamente.');
    }
}

function calculateNumberOfMonths(q0, p, j) {
    j = j / 100; // Converte taxa de juros para decimal
    let n = Math.log(p / (p - j * q0)) / Math.log(1 + j);
    return Math.ceil(n); // Arredonda para cima
}

function calculateMonthlyInterestRate(q0, p, n, tolerance = 0.000001) {
    let jLow = 0;
    let jHigh = 1;
    let jMid = (jLow + jHigh) / 2;

    while ((jHigh - jLow) > tolerance) {
        let calculatedP = (jMid * q0) / (1 - Math.pow(1 + jMid, -n));
        if (calculatedP > p) {
            jHigh = jMid;
        } else {
            jLow = jMid;
        }
        jMid = (jLow + jHigh) / 2;
    }
        
    return jMid * 100; // Converte de decimal para porcentagem
}

function calculateInstallment(q0, n, j) {
    j = j / 100; // Converte taxa de juros para decimal
    let p = (j * q0) / (1 - Math.pow(1 + j, -n));
    return p;
}

function calculateFinancedAmount(p, n, j) {
    j = j / 100; // Converte taxa de juros para decimal
    let q0 = (1 - Math.pow(1 + j, -n)) / j * p;
    return q0;
}

function calcularBancoCentral(mesesId, taxaJurosId, prestacaoId, financiadoId) {
    let numMeses = document.getElementById(mesesId).value;
    let taxaJuros = document.getElementById(taxaJurosId).value;
    let valorPrestacao = document.getElementById(prestacaoId).value;
    let valorFinanciado = document.getElementById(financiadoId).value;

    let emptyCount = [numMeses, taxaJuros, valorPrestacao, valorFinanciado].filter(x => x === "").length;

    if (emptyCount !== 1) {
        alert('Por favor, preencha exatamente 3 campos.');
        return;
    }

    if (numMeses === "") {
        let q0 = parseFloat(valorFinanciado);
        let p = parseFloat(valorPrestacao);
        let j = parseFloat(taxaJuros);
        let n = calculateNumberOfMonths(q0, p, j);
        document.getElementById(mesesId).value = n;
    } else if (taxaJuros === "") {
        let q0 = parseFloat(valorFinanciado);
        let p = parseFloat(valorPrestacao);
        let n = parseInt(numMeses);
        let j = calculateMonthlyInterestRate(q0, p, n);
        document.getElementById(taxaJurosId).value = j.toFixed(2);
    } else if (valorPrestacao === "") {
        let q0 = parseFloat(valorFinanciado);
        let n = parseInt(numMeses);
        let j = parseFloat(taxaJuros);
        let p = calculateInstallment(q0, n, j);
        document.getElementById(prestacaoId).value = p.toFixed(2);
    } else if (valorFinanciado === "") {
        let p = parseFloat(valorPrestacao);
        let n = parseInt(numMeses);
        let j = parseFloat(taxaJuros);
        let q0 = calculateFinancedAmount(p, n, j);
        document.getElementById(financiadoId).value = q0.toFixed(2);
    }
}

function limparBancoCentral(mesesId, taxaJurosId, prestacaoId, financiadoId) {
    document.getElementById(mesesId).value = "";
    document.getElementById(taxaJurosId).value = "";
    document.getElementById(prestacaoId).value = "";
    document.getElementById(financiadoId).value = "";
}

function imprimirBancoCentral() {
    window.print();
}
