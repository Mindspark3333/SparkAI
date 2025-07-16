import speech_recognition as sr
import os
from pydub import AudioSegment
import tempfile

def transcribe_audio(audio_file_path):
    """
    Transcribe audio file to text using Google Speech Recognition
    
    Args:
        audio_file_path (str): Path to the audio file
        
    Returns:
        str: Transcribed text or error message
    """
    try:
        # Initialize recognizer
        recognizer = sr.Recognizer()
        
        # Convert audio to WAV format if needed
        audio_path = convert_to_wav(audio_file_path)
        
        # Load audio file
        with sr.AudioFile(audio_path) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            # Record the audio
            audio_data = recognizer.record(source)
        
        # Perform speech recognition
        try:
            # Using Google Speech Recognition (free tier)
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError as e:
            return f"Could not request results from speech recognition service; {e}"
            
    except Exception as e:
        return f"Error processing audio: {str(e)}"
    finally:
        # Clean up temporary file if created
        if 'audio_path' in locals() and audio_path != audio_file_path:
            try:
                os.remove(audio_path)
            except:
                pass

def convert_to_wav(audio_file_path):
    """
    Convert audio file to WAV format if it's not already
    
    Args:
        audio_file_path (str): Path to the audio file
        
    Returns:
        str: Path to WAV file
    """
    try:
        # Check if file is already WAV
        if audio_file_path.lower().endswith('.wav'):
            return audio_file_path
        
        # Load audio file
        audio = AudioSegment.from_file(audio_file_path)
        
        # Create temporary WAV file
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_wav_path = temp_wav.name
        temp_wav.close()
        
        # Export as WAV
        audio.export(temp_wav_path, format="wav")
        
        return temp_wav_path
        
    except Exception as e:
        print(f"Error converting audio to WAV: {e}")
        return audio_file_path

def validate_audio_file(audio_file_path):
    """
    Validate if the audio file is readable and has content
    
    Args:
        audio_file_path (str): Path to the audio file
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        if not os.path.exists(audio_file_path):
            return False, "Audio file does not exist"
        
        if os.path.getsize(audio_file_path) == 0:
            return False, "Audio file is empty"
        
        # Try to load the audio file
        audio = AudioSegment.from_file(audio_file_path)
        
        if len(audio) == 0:
            return False, "Audio file has no content"
        
        if len(audio) < 100:  # Less than 0.1 seconds
            return False, "Audio file is too short"
        
        return True, "Audio file is valid"
        
    except Exception as e:
        return False, f"Error validating audio file: {str(e)}"

def get_audio_duration(audio_file_path):
    """
    Get the duration of an audio file in seconds
    
    Args:
        audio_file_path (str): Path to the audio file
        
    Returns:
        float: Duration in seconds, or 0 if error
    """
    try:
        audio = AudioSegment.from_file(audio_file_path)
        return len(audio) / 1000.0  # Convert milliseconds to seconds
    except Exception as e:
        print(f"Error getting audio duration: {e}")
        return 0.0

def compress_audio(audio_file_path, target_size_mb=5):
    """
    Compress audio file to reduce size while maintaining quality
    
    Args:
        audio_file_path (str): Path to the audio file
        target_size_mb (int): Target size in MB
        
    Returns:
        str: Path to compressed audio file
    """
    try:
        audio = AudioSegment.from_file(audio_file_path)
        
        # Get current file size
        current_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)
        
        if current_size_mb <= target_size_mb:
            return audio_file_path
        
        # Calculate compression ratio
        compression_ratio = target_size_mb / current_size_mb
        
        # Reduce bitrate and sample rate
        compressed_audio = audio.set_frame_rate(int(audio.frame_rate * compression_ratio))
        
        # Create compressed file
        compressed_path = audio_file_path.replace('.wav', '_compressed.wav')
        compressed_audio.export(compressed_path, format="wav", bitrate="64k")
        
        return compressed_path
        
    except Exception as e:
        print(f"Error compressing audio: {e}")
        return audio_file_path

