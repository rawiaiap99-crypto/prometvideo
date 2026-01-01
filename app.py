import streamlit as st
import google.generativeai as genai
import tempfile
import time
import os

st.set_page_config(page_title="محلل الفيديو", page_icon="🎬")

st.title("🎬 أداة تحليل الفيديو (Reverse Engineer)")
st.write("ارفع الفيديو وسأعطيك البرومبت، الإضاءة، والبرامج المستخدمة.")

# التحقق من وجود المفتاح
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.warning("⚠️ الرجاء وضع مفتاح API في إعدادات Secrets")
    st.stop()

uploaded_file = st.file_uploader("اختر فيديو (MP4)", type=["mp4", "mov"])

if uploaded_file is not None:
    st.video(uploaded_file)
    if st.button("تحليل الفيديو 🚀"):
        with st.spinner('جاري التحليل... يرجى الانتظار...'):
            try:
                # حفظ الملف مؤقتاً
                tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') 
                tfile.write(uploaded_file.read())
                
                # رفع الفيديو لجوجل
                video_file = genai.upload_file(path=tfile.name)
                
                # انتظار المعالجة
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)

                if video_file.state.name == "FAILED":
                    st.error("فشلت معالجة الفيديو من المصدر.")
                else:
                    # إرسال الطلب للذكاء الاصطناعي
                    model = genai.GenerativeModel('gemini-1.5-pro')
                    prompt = """
                    Analyze this video and provide a structured report in Arabic:
                    1. **Prompt (English):** Detailed prompt for Sora/Runway to recreate this.
                    2. **Style:** Visual style description.
                    3. **Lighting:** Lighting setup.
                    4. **Software:** Expected software used.
                    """
                    response = model.generate_content([video_file, prompt])
                    st.markdown(response.text)
                    
            except Exception as e:
                st.error(f"حدث خطأ: {e}")
