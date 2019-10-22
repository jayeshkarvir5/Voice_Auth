{% load i18n %}
var SpeechRecognition = window.webkitSpeechRecognition;

var recognition = new SpeechRecognition();

var Textbox1 = $('#ans1');
var Textbox2 = $('#ans2');
var Textbox3 = $('#ans3');
var Textbox4 = $('#ans4');
var instructions = $('instructions');

var flagl = 1;
{% get_current_language as langcode %}
{% if "hi" in langcode %}
    flagl = 1;
{% else %}
    flagl =0;
{% endif %}

if(flagl==1){
  recognition.lang = 'hi';
}

var Content = '';
var flag = 0;
recognition.continuous = false;

recognition.onresult = function(event) {
  var current = event.resultIndex;
  var transcript = event.results[current][0].transcript;

    Content += transcript;
    if(flag==0){
        Textbox1.val(Content);
    }else if(flag==1){
        Textbox2.val(Content);
    }else if(flag==2){
        Textbox3.val(Content);
    }else{
        Textbox4.val(Content);
    }
};

recognition.onstart = function() {
  instructions.text('Voice recognition is ON.');
}

recognition.onspeechend = function() {
  instructions.text('No activity.');
}

recognition.onerror = function(event) {
  if(event.error == 'no-speech') {
    instructions.text('Try again.');
  }
}

$('#start-btn1').on('click', function(e) {
    flag=0;
  if (Content.length) {
    Content = '';
  }
  recognition.start();
});
$('#start-btn2').on('click', function(e) {
   flag=1;
  if (Content.length) {
    Content = '';
  }
  recognition.start();
});
$('#start-btn3').on('click', function(e) {
    flag=2;
  if (Content.length) {
    Content = '';
  }
  recognition.start();
});
$('#start-btn4').on('click', function(e) {
    flag=3;
  if (Content.length) {
    Content = '';
  }
  recognition.start();
});
Textbox1.on('input', function() {
  Content = $(this).val();
})
Textbox2.on('input', function() {
  Content = $(this).val();
})
Textbox3.on('input', function() {
  Content = $(this).val();
})
Textbox4.on('input', function() {
  Content = $(this).val();
})
