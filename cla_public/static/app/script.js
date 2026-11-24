// Datepicker (vanillajs-datepicker) : chargé seulement si la page contient un champ date
(function () {
    var inputs = document.querySelectorAll('input[data-plugin="datepicker"]');
    if (!inputs.length) return;

    var base = 'https://cdn.jsdelivr.net/npm/vanillajs-datepicker@1.2.0/dist/';

    var css = document.createElement('link');
    css.rel = 'stylesheet';
    css.href = base + 'css/datepicker-bs4.min.css';
    document.head.appendChild(css);

    function loadScript(src, onload) {
        var script = document.createElement('script');
        script.src = src;
        script.onload = onload;
        document.head.appendChild(script);
    }

    // La locale fr a besoin de Datepicker : chargement l'un après l'autre
    loadScript(base + 'js/datepicker-full.min.js', function () {
        loadScript(base + 'js/locales/fr.js', function () {
            inputs.forEach(function (elem) {
                new Datepicker(elem, {
                    format: 'dd/mm/y',
                    language: 'fr'
                });
            });
        });
    });
})();
