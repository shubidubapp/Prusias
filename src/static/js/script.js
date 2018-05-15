$(document).ready(main);

function main() {
    $('.humanize').each(function () {
        $(this).html(humanFormat(parseInt($(this).html())))
    });
}
