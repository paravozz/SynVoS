$(document).ready(function () {
    $('.modal').modal();
});
stepers = [$('#stepper-1'), $('#stepper-2'),$('#stepper-3'),$('#stepper-4')];
$('#step2').hide();
$('#step3').hide();
$('#step4').hide();
$('#circle').hide();
$('#progress').hide();
$('#wav-status').hide();
$('#play-button').hide();
$('#waveform').hide();
$('#region-done').hide();
var wave_success = false;
var text_success = false;
var text_bar_count = 0;
var loop_region;
var processed_wav;
var textarea = $('#song-text');
var wavesurfer = undefined;
var result_url = '';

function upload(file) {
     var xhr = new XMLHttpRequest();
     wave_success = false;
     var percentage = 0;

     // обработчик для закачки
     xhr.upload.onprogress = function (event) {
         percentage = (100 * event.loaded) / event.total;
         $('#bar').css("width", percentage + "%");
         $('#wav-status').text("Отправка файла...");

         if (percentage == 100) {
             Materialize.toast('Файл отправлен.', 1000);
             $('#progress').hide();
             Materialize.toast('Обработка файла...', 2500);
             $('#wav-status').text("Обработка файла...");
             $('#circle').show();
             $('#bar').css("width", "0");
         }
     };
     // обработчики успеха и ошибки
     // если status == 200, то это успех, иначе ошибка
     xhr.onload = xhr.onerror = function () {
         if (this.status == 200) {
             Materialize.toast('Файл обработан успешно.', 2000);
             $('#wav-status').text("Успешно!");
             $('#circle').hide();
             processed_wav = JSON.parse(xhr.responseText);
             wave_success = true;
             stepers[0].addClass('step-done');
             stepers[1].addClass('active-step');
             $('#step1').hide();
             $('#step2').show();
         } else {
             $('#progress').hide();
             $('#circle').hide();
             $('#play-button').hide();
             $('#waveform').hide();
             $('#wav-status').hide();
             Materialize.toast("Ошибка загрузки." + this.status, 2000);
             Materialize.toast("Пожалуйста, обновите страницу и попробуйте снова." + this.status, 2000);
             $('#loader').show();
             wave_success = false;
                     // away_come(stepes[0], stepers[1]);
             stepers[0].removeClass('step-done');
             stepers[1].removeClass('active-step');
         }
     };

     xhr.open("POST", "file_upload", true);
     $('#progress').show();
     $('#wav-status').show();
     $('#loader').hide();
     xhr.send(file);
}

 $('#submit-song').click(function() {
    event.preventDefault();
     if ($('#file-loader').get(0).files.length == 0) {
         Materialize.toast('Пожалуйста, выберите файл.', 2000);
     } else {
         $('#wav-status').hide();
         $('#waveform').hide();
         var input = $('#file-loader').get(0);
         var file = input.files[0];

         if (file) {
             var form = $('#file-load-form')[0];
             var form_data = new FormData(form);
             upload(form_data)
         }
         return false;
     }
  });

 textarea.keyup(function() {
    var lines = textarea.val().split("\n");

    if (textarea.val().length > 0) {
        text_bar_count = lines.length;
                // text_bar_count = Math.ceil(lines.length / 4);
        $('#bar-counter').text(text_bar_count);
    } else {
        text_bar_count = 0;
        $('#bar-counter').text(text_bar_count);

    }

    for (var i = 0; i < lines.length; i++) {
        lines[i] = lines[i][0].toUpperCase() + lines[i].slice(1);
        if (lines[i].length <= 32) continue;
        var j = 0;
        var space = 32;
        while (j++ <= 32) {
            if (lines[i].charAt(j) === " ") space = j;
        }
        lines[i + 1] = lines[i].substring(space + 1) + (lines[i + 1] || "");
        lines[i] = lines[i].substring(0, space);
    }
    textarea.val(lines.join("\n"));
        // textarea.val(lines.slice(0, 4).join("\n"));
 });

 $('#text_done').click(function () {
    if (textarea.val().length == 0) {
        Materialize.toast('Пожалуйста заполните поле текста', 1000);
    } else {
        var isCyrillic = function (text) {
            return /[а-я]/i.test(text);
        };
        var lines = textarea.val().split("\n");
        var lang = isCyrillic(textarea.val()) ? 'ru-RU' : 'en-US';
        var speaker = $('#voice-select').prop('checked') ? 'jane' : 'zahar';
        var reqdata = {
            'lines': lines,
            'lang': lang,
            'speaker': speaker
        };
        text_success = false;
        Materialize.toast('Обработка текста...', 2000);
        $.post({
            url: '/text_generated',
            data: JSON.stringify(reqdata),
            dataType: 'json',
            contentType: 'application/json; charset=utf-8',
            success: function () {
                Materialize.toast('Текст обработан успешно.', 2000);
                text_success = true;
                stepers[1].addClass('step-done');
                stepers[2].addClass('active-step');
                $('#step2').hide();
                $('#step3').show();
            },
            error: function () {
                stepers[1].removeClass('step-done');
                Materialize.toast('Ошибка обработки текста', 2000);
                text_success = false;
                stepers[2].removeClass('active-step');
            }
        });

        if (text_success == true) {
            Materialize.toast("Пожалуйста, заполните поле текста или исправьте ошибки ввода", 1000);
        } else if (wave_success == false) {
            Materialize.toast("Пожалуйста, подождите пока обработается файл", 1000);
        } else {
            if (wavesurfer != undefined) {
                wavesurfer.empty();
                $('#waveform').html("");
                $('#play-button').hide();
                $('#region-done').hide();
            }

            wavesurfer = WaveSurfer.create({
                container: '#waveform',
                waveColor: 'violet',
                progressColor: 'purple',
                splitChannels: processed_wav.stereo
            });

            wavesurfer.on('ready', function () {
                loop_region = wavesurfer.addRegion({
                    loop: true,
                    resize: false,
                    start: 0,
                    end: processed_wav.bar_len * text_bar_count
                });
                $('#play-button').show();
                $('#play-button').unbind('click');
                $('#play-button').bind('click', function () {
                    wavesurfer.playPause();
                });
            });

            $(window).resize(function () {
                wavesurfer.empty();
                wavesurfer.drawBuffer();
            });

            $('#waveform').show();
            $('#region-done').show();
            wavesurfer.load(processed_wav.file);
        }
    }
 });

 $('#region-done').click(function () {
     var region = {
         'start': loop_region.start,
         'end': loop_region.end
     };
     Materialize.toast('Обработка файла...', 2000);
     $.post({
        url: '/region_done',
        data: JSON.stringify(region),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        success: function (response) {
            result_url = response
            Materialize.toast('Готово!', 2000);
            stepers[2].addClass('step-done');
            stepers[3].addClass('active-step');
            $('#step3').hide();
            $('#step4').show();
            $('#audio-result').attr('src', result_url);
            $('#audio-href').attr('href', result_url);
            if (wavesurfer.isPlaying) {
                wavesurfer.pause();
            }
        },
        error: function() {
            stepers[2].removeClass('step-done');
            stepers[3].removeClass('active-step');
            Materialize.toast('Ошибка. Попробуйте перезагрузить страницу и повторить', 4000);
        }
     });
 });
$('#save-audio').click(function () {
    event.preventDefault();
    $.post({
        url: '/savetodb',
        data: JSON.stringify(result_url),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        success: function (response) {
            window.location.replace(response);
        }
    });
});