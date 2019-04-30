const forceStr = 'petty\'s mom ';
const forceStrLen = forceStr.length;

$('#myTextBox').keydown(function(event) {
  event.preventDefault();
  event.stopPropagation();
  const currentStrLen = $(this).val().length;
  const repetitions = Math.floor(currentStrLen / forceStrLen);
  const newSlot = currentStrLen % forceStrLen;
  $(this).val(forceStr.repeat(repetitions) + forceStr.substr(0, newSlot + 1));
});
