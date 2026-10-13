#!/usr/bin/env python3
"""Extract the reversed PCMU call from the challenge PCAP into a WAV file."""

from __future__ import annotations

import struct
import wave
from pathlib import Path

from scapy.all import UDP, rdpcap


HERE = Path(__file__).resolve().parent
PCAP = HERE.parent / "distfiles" / "welcomecall.pcap"
OUTPUT = HERE / "reversed.wav"
RTP_PORTS = (4000, 4002)
SAMPLE_RATE = 8000


def rtp_payload(packet: bytes) -> tuple[int, bytes] | None:
    if len(packet) < 12 or packet[0] >> 6 != 2:
        return None

    payload_type = packet[1] & 0x7F
    if payload_type != 0:  # G.711 μ-law / PCMU
        return None

    sequence = struct.unpack_from("!H", packet, 2)[0]
    offset = 12 + (packet[0] & 0x0F) * 4  # CSRC list

    if packet[0] & 0x10:  # RTP extension
        if len(packet) < offset + 4:
            return None
        extension_words = struct.unpack_from("!H", packet, offset + 2)[0]
        offset += 4 + extension_words * 4

    end = len(packet)
    if packet[0] & 0x20:  # RTP padding
        padding = packet[-1]
        if padding == 0 or padding > end - offset:
            return None
        end -= padding

    if offset >= end:
        return None
    return sequence, packet[offset:end]


def mulaw_sample(value: int) -> int:
    value = (~value) & 0xFF
    magnitude = ((value & 0x0F) << 3) + 0x84
    magnitude <<= (value >> 4) & 0x07
    return magnitude - 0x84 if value & 0x80 else 0x84 - magnitude


def main() -> None:
    chunks: list[tuple[int, bytes]] = []
    for frame in rdpcap(str(PCAP)):
        if UDP not in frame:
            continue
        udp = frame[UDP]
        if (udp.sport, udp.dport) != RTP_PORTS:
            continue
        parsed = rtp_payload(bytes(udp.payload))
        if parsed is not None:
            chunks.append(parsed)

    if not chunks:
        raise SystemExit("No RTP/PCMU packets found on UDP 4000 -> 4002")

    chunks.sort(key=lambda item: item[0])
    ulaw = b"".join(payload for _, payload in chunks)
    pcm = [mulaw_sample(value) for value in ulaw]
    reversed_pcm = struct.pack(f"<{len(pcm)}h", *reversed(pcm))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUTPUT), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(reversed_pcm)

    print(f"RTP packets: {len(chunks)}")
    print(f"PCMU payload bytes: {len(ulaw)}")
    print(f"Wrote reversed-time audio: {OUTPUT}")


if __name__ == "__main__":
    main()
