$(document).ready(function() {
    $('.inline-svg-container').each(function(i, el) {
        var element = $(el);
        $.get(element.attr('data-src'), function (rep) {
            console.log(rep.querySelector("svg"));
            element.append(rep.querySelector("svg"))
        })
    });
})