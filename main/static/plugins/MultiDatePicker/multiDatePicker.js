window.clone_out = (subject) ->
  $subject = $(subject)
  $($subject.html()).appendTo('body')
  $subject.remove()
  $('.ui-datepicker-calendar > tbody > tr > td a.ui-state-default').click(stop_it)

window.stop_it = (e) ->
  console.log('hey', @)
  $(@).toggleClass('ui-state-active')
  #e.preventDefault()
  e.stopPropagation()
  false

just_stop = (e) ->
  e.stopPropagation()
  false

$('body').on('click', '.ui-datepicker-calendar > tbody > tr > td a.ui-state-default', stop_it)

$('.ui-datepicker-calendar > tbody > tr > td a.ui-state-default').click(stop_it)
