(function () {
    $('input[data-plugin="datepicker"]').each(function (i, elem) {
        new Datepicker(elem, {
            format: 'dd/mm/y',
            language: 'fr'
        });
    })
})()