from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired

#-=========================================================
import wave, math, contextlib
import speech_recognition as sr
from moviepy.editor import AudioFileClip
#==========================================================

from run import generate_summary


app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/files'

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

@app.route('/', methods=['GET',"POST"])
@app.route('/home', methods=['GET',"POST"])
def home():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data # First grab the file
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename))) # Then save the file
        flash('File(s) successfully uploaded')
        #===========================================================
        transcribed_audio_file_name = "transcribed_speech.wav"
        print(file.filename)
        print("\n")
        file_n = file.filename
        zoom_video_file_name = f'static/files/{file_n}'
        audioclip = AudioFileClip(zoom_video_file_name)
        audioclip.write_audiofile(transcribed_audio_file_name)
        with contextlib.closing(wave.open(transcribed_audio_file_name,'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
        total_duration = math.ceil(duration / 60)
        r = sr.Recognizer()
        transcript = ""
        for i in range(0, total_duration):
            with sr.AudioFile(transcribed_audio_file_name) as source:
                audio = r.record(source, offset=i*60, duration=60)
            f = open("transcription.txt", "a")
            transcript+=r.recognize_google(audio)
            print(r.recognize_google(audio))
            f.write(r.recognize_google(audio))
            f.write(" ")
        print(transcript)
        f.close()

        summary = ""
        
        summary = generate_summary(transcript)

        results = [transcript, summary]

        #===========================================================
        return render_template('results.html', form=form, results=results)
        #return "File has been uploaded."
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)







