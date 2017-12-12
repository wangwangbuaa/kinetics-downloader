import argparse, os, librosa
import tensorflow as tf

import lib.config as config
import lib.utils as utils

kinetics_sound_400_train = utils.load_json("resources/kinetics_full_sound_400_train.json")
kinetics_sound_400_valid = utils.load_json("resources/kinetics_full_sound_400_val.json")
kinetics_classes = utils.load_json("resources/kinetics_full_sound_400_classes.json")
sampling_rate = 22050

def load_audio(path):
  audio, _ = librosa.load(path, sr=sampling_rate, mono=True)
  return audio

def bytes_feature(value):
  return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

def int64_feature(value):
  return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

def convert_to_tfrecord(meta, classes, root, records_path):

  writer = tf.python_io.TFRecordWriter(records_path)

  i = 0
  for path, cls_name in meta.items():

    if i > 0 and i % 100 == 0:
      print(i)

    cls_id = classes[cls_name]

    audio = load_audio(os.path.join(root, cls_name.replace(" ", "_"), path + ".mp3"))
    audio_raw = audio.tostring()

    length = audio.shape[0]

    example = tf.train.Example(features=tf.train.Features(feature={
      "length": int64_feature(length),
      "sound_raw": bytes_feature(audio_raw),
      "cls_id": int64_feature(cls_id)}))

    writer.write(example.SerializeToString())
    i += 1

  writer.close()

def main(args):

  # TODO: finish

  convert_to_tfrecord(kinetics_sound_400_train, kinetics_classes, config.TRAIN_SOUND_ROOT, "dataset/kinetics_full_sound_400_train.tfrecords")
  convert_to_tfrecord(kinetics_sound_400_valid, kinetics_classes, config.VALID_SOUND_ROOT, "dataset/kinetics_full_sound_400_val.tfrecords")

parser = argparse.ArgumentParser()
parser.add_argument("subset", help="train, valid or test")
parser.add_argument("save_path", help="tfrecords file save path")
parsed = parser.parse_args()
main(parsed)
