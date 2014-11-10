$(function () {
  $('.list-group-item').hover(function () {
    $(this).find('.remove-item').toggle();
  });
  $('#query').on('keyup', function () {
    if ($(this).val().length != 0) {
      $('.btn-search').attr('disabled', false);
    } else {
      $('.btn-search').attr('disabled', true);
    }
  });
});
