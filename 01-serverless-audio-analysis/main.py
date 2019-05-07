from scipy.io import wavfile
import tempfile
import uuid
import librosa
import numpy as np

from google.cloud import storage
from google.cloud import firestore

storage_client = storage.Client()
db = firestore.Client()

def analyze_sound(event, context):
    file_data = event

    file_name = file_data['name']
    bucket_name = file_data['bucket']

    blob = storage_client.bucket(bucket_name).get_blob(file_name)
	
    blob_name = blob.name
    _, temp_local_filename = tempfile.mkstemp()

    # Download file from bucket.
    blob.download_to_filename(temp_local_filename)
    
    y, sr = librosa.load(temp_local_filename)

    y_mono = librosa.to_mono(y)
    y_mono_22050 = librosa.resample(y_mono, sr, 22050)
    mfccs = librosa.feature.mfcc(y=y_mono_22050, sr=22050, n_mfcc=12)

    mean_mfccs = [np.mean(mfcc) for mfcc in mfccs] 

    
    print(f'Audio file name: {file_name}')
    
    print(f'Audio file is {len(y)} samples long.')

    uid = uuid.uuid4()
    doc_ref = db.collection(u'sounds').document(str(uid))
    doc_ref.set({
        u'uid': str(uid),
        u'blob_name': blob_name,
        u'file_name': file_name,
        u'length': len(y),
        u'mean_mfccs': mean_mfccs
    })
