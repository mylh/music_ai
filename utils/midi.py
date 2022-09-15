import os
import logging
from shutil import copyfile

import click
from fastprogress.fastprogress import progress_bar
from mido import MidiFile, MidiTrack, Message

logging.basicConfig()

log = logging.getLogger(__name__)


@click.group()
def cli():
    pass


def extract_track(src_dir, fname, track_num=1, dst_dir='./out/'):
    """Extracts track from a midi file and writes a new file in dst_dir
    Also copies track number 0 since it usually contains tempo and other meta
    information
    """
    log.debug("Processing %s", fname)
    fpath = os.path.join(src_dir, fname)
    outpath = os.path.join(dst_dir, fname)
    mid = MidiFile(fname)
    if mid.type == 0:
        log.debug('File %s type is 0, writing without modifications', fname)
        copyfile(fpath, outpath)
        return True
    elif mid.type == 2:
        log.debug('File %s is 2 and is not supported', fname)
        return False
    if mid.tracks == 0:
        log.error("Midi file %s does not contain tracks", fname)
        return False

    out = MidiFile(type=1, ticks_per_beat=mid.ticks_per_beat)
    out.tracks.append(mid.tracks[0])
    out.tracks.append(mid.tracks[track_num])
    out.save(outpath)
    return True


@cli.command()
@click.argument('src_dir', type=click.Path(exists=True, file_okay=False))
@click.option('--out_dir', type=click.Path(exists=True, file_okay=False),
              default='./out/')
@click.option('--track', type=int, default=1)
def extract_melodies(src_dir, out_dir, track):
    midi_files = []
    for fname in os.listdir(src_dir):
        if not fname.endswith('.mid'):
            continue
        fpath = os.path.join(src_dir, fname)
        if not os.path.isfile(fpath):
            continue
        midi_files.append(fname)
    for i in progress_bar(range(len(midi_files))):
        extract_track(src_dir, midi_files[i], track_num=track, dst_dir=out_dir)


if __name__ == '__main__':
    cli()
