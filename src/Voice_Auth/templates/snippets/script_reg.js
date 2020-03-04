{% load i18n %}

var flag = 0;

URL = window.URL || window.webkitURL;

var gumStream; 						//stream from getUserMedia()
var rec; 							//Recorder.js object
var input; 							//MediaStreamAudioSourceNode we'll be recording

// shim for AudioContext when it's not avb.
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext; //audio context to help us record
var recordButton;
var stopButton;

var Textbox;
var flag;
$('#start-btn1').on('click', function(e){
    flag = '1';
    recordButton = document.getElementById("start-btn2");
    recordButton.disabled = true;
    recordButton = document.getElementById("start-btnpw");
    recordButton.disabled = true;
    recordButton = document.getElementById("start-btncpw");
    recordButton.disabled = true;
    recordButton = document.getElementById("start-btn1");
    stopButton = document.getElementById("stop-btn1");
    Textbox = $('#ans1');
    //add events to those 2 buttons
    startRecording();
    stopButton.addEventListener("click", stopRecording);
});
$('#start-btn2').on('click', function(e){
    flag = '2';
    recordButton = document.getElementById("start-btn1");
    recordButton.disabled = true;
    recordButton = document.getElementById("start-btnpw");
    recordButton.disabled = true;
    recordButton = document.getElementById("start-btncpw");
    recordButton.disabled = true;
    recordButton = document.getElementById("start-btn2");
    stopButton = document.getElementById("stop-btn2");
    Textbox = $('#ans2');
    //add events to those 2 buttons
    startRecording();
    stopButton.addEventListener("click", stopRecording);
});
$('#start-btnpw').on('click', function(e){
    flag = '3';
    recordButton = document.getElementById("start-btn1");
    recordButton.disabled = true;
    recordButton = document.getElementById("start-btncpw");
    recordButton.disabled = true;
    recordButton = document.getElementById("start-btn2");
    recordButton.disabled = true;
    recordButton = document.getElementById("start-btnpw");
    stopButton = document.getElementById("stop-btnpw");
    Textbox = $('#pw1');
    //add events to those 2 buttons
    startRecording();
    stopButton.addEventListener("click", stopRecording);
});
$('#start-btncpw').on('click', function(e){
    flag = '4';
    recordButton = document.getElementById("start-btn1");
    recordButton.disabled = true;
    recordButton = document.getElementById("start-btnpw");
    recordButton.disabled = true;
    recordButton = document.getElementById("start-btn2");
    recordButton.disabled = true;
    recordButton = document.getElementById("start-btncpw");
    stopButton = document.getElementById("stop-btncpw");
    Textbox = $('#pw2');
    //add events to those 2 buttons
    startRecording();
    stopButton.addEventListener("click", stopRecording);
});

function startRecording() {
    console.log("recordButton clicked");
    var constraints = { audio: true, video:false }
    // Disable the record button until we get a success or fail from getUserMedia()

    recordButton.disabled = true;
    stopButton.disabled = false;

    navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
        console.log("getUserMedia() success, stream created, initializing Recorder.js ...");

        /*
            create an audio context after getUserMedia is called
            sampleRate might change after getUserMedia is called, like it does on macOS when recording through AirPods
            the sampleRate defaults to the one set in your OS for your playback device
        */
        audioContext = new AudioContext();

        /*  assign to gumStream for later use  */
        gumStream = stream;

        /* use the stream */
        input = audioContext.createMediaStreamSource(stream);

        /*
            Create the Recorder object and configure to record mono sound (1 channel)
            Recording 2 channels  will double the file size
        */
        rec = new Recorder(input,{numChannels:1})

        //start the recording process
        rec.record()

        console.log("Recording started");

    }).catch(function(err) {
        //enable the record button if getUserMedia() fails
        recordButton.disabled = false;
        stopButton.disabled = true;
    });
}

function stopRecording() {
    console.log("stopButton clicked");

    //disable the stop button, enable the record too allow for new recordings

    stopButton.disabled = true;

    //tell the recorder to stop the recording
    rec.stop();

    //stop microphone access
    gumStream.getAudioTracks()[0].stop();

    //create the wav blob and pass it on to createDownloadLink
    rec.exportWAV(uploadAudio);
}

function uploadAudio(blob) {
    var form = new FormData();
    var username = $('#un').val();
    var no_ = flag;
    var filename = "a" + flag + ".wav";
    form.append('audio', blob, filename);
    form.append('username', username);
    form.append('no_', no_);
    form.append('csrfmiddlewaretoken', "{{ csrf_token }}");
    console.log(blob);
    $.ajax({
        type: 'POST',
        url: '{% url "save_audio" %}',
        data: form,
        dataType: 'json',
        processData: false,
        contentType: false,
        success: function (data) {
          if (data.success) {
            Textbox.val(data.text);
            alert('Saved audio.');
          }else{
             alert("Could not recognise");
          }
        }
    });
    recordButton = document.getElementById("start-btn1");
    recordButton.disabled = false;
    recordButton = document.getElementById("start-btn2");
    recordButton.disabled = false;
    recordButton = document.getElementById("start-btnpw");
    recordButton.disabled = false;
    recordButton = document.getElementById("start-btncpw");
    recordButton.disabled = false;
}
