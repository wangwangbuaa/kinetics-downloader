import argparse, os, librosa
import tensorflow as tf

import lib.config as config
import lib.constants as constants
import lib.utils as utils

def load_audio(path, sampling_rate):
  """
  Load audio using librosa library.
  :param path:            Path to the audio file.
  :param sampling_rate:   Sampling rate to convert all audios to.
  :return:                Audio data.
  """
  audio, _ = librosa.load(path, sr=sampling_rate, mono=True)
  return audio

def bytes_feature(value):
  """
  Get a byte feature Tensor.
  :param value:
  :return:
  """
  return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

def int64_feature(value):
  """
  Get an int64 feature Tensor.
  :param value:
  :return:
  """
  return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

def convert_to_tfrecords(meta, classes, root, records_path, sampling_rate, class_dirs=True):
  """
  Pack sound files into a tfrecords file.
  Some of the code was taken from http://warmspringwinds.github.io/tensorflow/tf-slim/2016/12/21/tfrecords-guide/.
  :param meta:              Sound metadata (generated by create_meta.py).
  :param classes:           Dataset classes.
  :param root:              Root of the folder where the sound files were downloaded.
  :param records_path:      Where to save the tfrecords file.
  :param sampling_rate:   Sampling rate to convert all audios to.
  :param class_dirs:        Expect sounds to be located in folders named after their classes (e.g. jogging/0123.mp3).
  :return:
  """

  writer = tf.python_io.TFRecordWriter(records_path)

  i = 0
  for path, cls_name in meta.items():

    if i > 0 and i % 100 == 0:
      print(i)

    if class_dirs:
      cls_id = classes[cls_name]
      file_path = os.path.join(root, utils.class_name_to_dir_name(cls_name), path + ".mp3")
    else:
      cls_id = 0
      file_path = os.path.join(root, path + ".mp3")

    audio = load_audio(file_path, sampling_rate)
    audio_raw = audio.tostring()

    length = audio.shape[0]

    example = tf.train.Example(features=tf.train.Features(feature={
      "path": bytes_feature(file_path.encode()),
      "length": int64_feature(length),
      "sound_raw": bytes_feature(audio_raw),
      "cls_id": int64_feature(cls_id)}))

    writer.write(example.SerializeToString())
    i += 1

  writer.close()

def main(args):

  if args.subset == constants.TRAIN:
    root = config.TRAIN_SOUND_ROOT
    cls_dirs = True
  elif args.subset == constants.VALID:
    root = config.VALID_SOUND_ROOT
    cls_dirs = True
  elif args.subset == constants.TEST:
    root = config.TEST_SOUND_ROOT
    cls_dirs = False
  else:
    raise ValueError("Invalid subset.")

  convert_to_tfrecords(utils.load_json(args.meta_path), utils.load_json(args.classes_path), root, args.save_path,
                       args.sampling_rate, class_dirs=cls_dirs)

parser = argparse.ArgumentParser("Pack all sound files into a single tfrecords (a Tensorflow file format).")

parser.add_argument("subset", help="{}, {} or {}".format(constants.TRAIN, constants.VALID, constants.TEST))
parser.add_argument("meta_path", help="metadata path")
parser.add_argument("classes_path", help="classes path")
parser.add_argument("save_path", help="tfrecords file save path")
parser.add_argument("--sampling-rate", type=int, default=22050, help="sampling rate to convert all audios to")

parsed = parser.parse_args()
main(parsed)
