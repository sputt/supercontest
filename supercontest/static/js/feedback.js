const forceStr = "petty's mom ";
const forceStrLen = forceStr.length;

$("#myTextBox").keydown(function(event) {
    event.preventDefault();
    event.stopPropagation();
    let currentStrLen = $(this).val().length;
    let repetitions = Math.floor(currentStrLen / forceStrLen);
    let newSlot = currentStrLen % forceStrLen;
    $(this).val(forceStr.repeat(repetitions) + forceStr.substr(0, newSlot + 1));
});