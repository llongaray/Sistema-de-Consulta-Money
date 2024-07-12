// Funções adicionais (sem alterações)
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

    if (numMeses !== "" && taxaJuros !== "" && valorPrestacao !== "") {
        valorFinanciado = calculateFinancedAmount(valorPrestacao, numMeses, taxaJuros);
        document.getElementById(financiadoId).value = 'R$ ' + valorFinanciado.toFixed(2);
    } else if (numMeses !== "" && valorPrestacao !== "" && valorFinanciado === "") {
        taxaJuros = calculateMonthlyInterestRate(valorPrestacao, valorFinanciado, numMeses);
        document.getElementById(taxaJurosId).value = taxaJuros.toFixed(2) + ' %';
    } else if (numMeses !== "" && valorPrestacao === "" && valorFinanciado !== "") {
        valorPrestacao = calculateInstallment(valorFinanciado, numMeses, taxaJuros);
        document.getElementById(prestacaoId).value = 'R$ ' + valorPrestacao.toFixed(2);
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
