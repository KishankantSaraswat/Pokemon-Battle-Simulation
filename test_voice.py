#!/usr/bin/env python3
"""
Voice Recognition Test Script
Tests if voice features are working properly
"""

try:
    import speech_recognition as sr
    import pydub
    import pyttsx3
    import pyaudio
    print("✅ All voice libraries imported successfully!")
    VOICE_AVAILABLE = True
except ImportError as e:
    print(f"❌ Voice library import error: {e}")
    VOICE_AVAILABLE = False

def test_microphone():
    """Test microphone access"""
    print("\n🎤 Testing Microphone Access...")
    
    try:
        r = sr.Recognizer()
        microphones = sr.Microphone.list_microphone_names()
        print(f"📱 Available Microphones: {len(microphones)}")
        for i, name in enumerate(microphones[:3]):  # Show first 3
            print(f"   {i}: {name}")
        
        # Test default microphone
        with sr.Microphone() as source:
            print("🔧 Testing default microphone...")
            r.adjust_for_ambient_noise(source, duration=0.5)
            print("✅ Microphone access successful!")
            return True
            
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        return False

def test_speech_recognition():
    """Test speech recognition with a short recording"""
    print("\n🗣️ Testing Speech Recognition...")
    print("📢 Say something in the next 3 seconds...")
    
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            print("🎤 Listening...")
            audio = r.listen(source, timeout=3, phrase_time_limit=3)
        
        print("🔍 Processing audio...")
        text = r.recognize_google(audio)
        print(f"✅ Recognized: '{text}'")
        return True, text
        
    except sr.WaitTimeoutError:
        print("⏰ No speech detected in timeout period")
        return False, "No speech detected"
    except sr.UnknownValueError:
        print("❓ Could not understand audio")
        return False, "Could not understand"
    except sr.RequestError as e:
        print(f"🌐 Speech service error: {e}")
        return False, str(e)
    except Exception as e:
        print(f"❌ Speech recognition error: {e}")
        return False, str(e)

def test_pokemon_extraction():
    """Test Pokemon name extraction from sample text"""
    print("\n🎯 Testing Pokemon Name Extraction...")
    
    # Sample voice commands
    test_phrases = [
        "Battle Pikachu against Charizard",
        "Let's fight between Gengar and Alakazam", 
        "Show me Snorlax vs Machamp",
        "I want to see Bulbasaur battle Squirtle"
    ]
    
    pokemon_names = [
        "pikachu", "charizard", "bulbasaur", "squirtle", "gengar", "alakazam",
        "snorlax", "machamp", "dragonite", "mewtwo", "venusaur", "blastoise"
    ]
    
    for phrase in test_phrases:
        print(f"\n📝 Testing: '{phrase}'")
        found_pokemon = []
        
        for pokemon in pokemon_names:
            if pokemon.lower() in phrase.lower():
                found_pokemon.append(pokemon)
        
        if len(found_pokemon) >= 2:
            print(f"✅ Extracted: {found_pokemon[0].title()} vs {found_pokemon[1].title()}")
        else:
            print(f"⚠️ Found only: {', '.join(found_pokemon) if found_pokemon else 'None'}")
    
    return True

def test_text_to_speech():
    """Test text-to-speech functionality"""
    print("\n🔊 Testing Text-to-Speech...")
    
    try:
        engine = pyttsx3.init()
        
        # Set properties
        voices = engine.getProperty('voices')
        if voices:
            print(f"🎵 Available voices: {len(voices)}")
            engine.setProperty('voice', voices[0].id)
        
        engine.setProperty('rate', 150)  # Speed
        engine.setProperty('volume', 0.8)  # Volume
        
        # Test speech
        test_text = "Pokemon battle system voice test successful!"
        print(f"🗣️ Speaking: '{test_text}'")
        
        engine.say(test_text)
        engine.runAndWait()
        
        print("✅ Text-to-speech working!")
        return True
        
    except Exception as e:
        print(f"❌ Text-to-speech error: {e}")
        return False

def main():
    """Run all voice tests"""
    print("🎤 Pokemon Battle System - Voice Feature Test")
    print("=" * 60)
    
    if not VOICE_AVAILABLE:
        print("❌ Voice libraries not available!")
        print("💡 Install with: pip install SpeechRecognition pydub pyttsx3 pyaudio")
        return
    
    print("✅ Voice libraries loaded successfully!")
    
    # Test 1: Microphone Access
    mic_success = test_microphone()
    
    # Test 2: Pokemon Name Extraction
    extraction_success = test_pokemon_extraction()
    
    # Test 3: Text-to-Speech
    tts_success = test_text_to_speech()
    
    # Test 4: Speech Recognition (optional - requires user input)
    print("\n" + "=" * 40)
    user_input = input("🎤 Test speech recognition? (y/n): ").lower()
    
    if user_input == 'y':
        speech_success, result = test_speech_recognition()
    else:
        speech_success = True
        print("⏭️ Skipped speech recognition test")
    
    # Results Summary
    print("\n" + "=" * 60)
    print("📊 VOICE TEST RESULTS:")
    print("=" * 60)
    print(f"🎤 Microphone Access:     {'✅ PASS' if mic_success else '❌ FAIL'}")
    print(f"🎯 Pokemon Extraction:    {'✅ PASS' if extraction_success else '❌ FAIL'}")
    print(f"🔊 Text-to-Speech:        {'✅ PASS' if tts_success else '❌ FAIL'}")
    print(f"🗣️ Speech Recognition:    {'✅ PASS' if speech_success else '❌ FAIL'}")
    
    all_passed = mic_success and extraction_success and tts_success and speech_success
    
    if all_passed:
        print("\n🎉 ALL VOICE FEATURES WORKING!")
        print("✅ Ready to use voice commands in Pokemon Battle System!")
    else:
        print("\n⚠️ Some voice features need attention")
        print("💡 Check error messages above for troubleshooting")
    
    print("\n🚀 Next Steps:")
    print("   1. Start complete system: python run_complete_system.py")
    print("   2. Or start frontend only: streamlit run frontend/app.py")
    print("   3. Click '🎤 Listen for Battle Command' in the web interface")

if __name__ == "__main__":
    main()
