// news-image-20261124 entry program (Node 22, standard library only).
//
// Validates the entry.png shipped beside this file with a from-scratch PNG
// walk — hand-rolled CRC-32, chunk-by-chunk — and only then copies it to
// /output/entry.png (or $MAKEFUN_OUTPUT_DIR). Any structural defect fails
// loudly instead of shipping a broken file.
//
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
//
// The image itself is drawn by draw.py in this same repository; this program
// never writes pixels, it only checks and copies, so both runs produce the
// same bytes.

import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { inflateSync } from 'node:zlib';
import { fileURLToPath } from 'node:url';

const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const MAX_BYTES = 1048576;
const MAX_DIM = 1024;

interface ChunkInfo {
  type: string;
  offset: number;
  length: number;
  crcOk: boolean;
}

interface ValidationReport {
  file: string;
  bytes: number;
  width: number;
  height: number;
  bitDepth: number;
  colorType: number;
  chunks: ChunkInfo[];
  idatBytes: number;
  idatInflatedBytes: number;
  checks: Record<string, boolean>;
}

// --- CRC-32 (IEEE 802.3, polynomial 0xEDB88320), table built at startup. ---
const CRC_TABLE: Uint32Array = (() => {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) {
      c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    }
    table[n] = c >>> 0;
  }
  return table;
})();

function crc32(buf: Buffer, start: number, end: number): number {
  let c = 0xffffffff;
  for (let i = start; i < end; i++) {
    c = CRC_TABLE[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  }
  return (c ^ 0xffffffff) >>> 0;
}

function readU32BE(buf: Buffer, off: number): number {
  return buf.readUInt32BE(off);
}

class PngValidator {
  private readonly data: Buffer;
  private readonly problems: string[] = [];
  private readonly chunks: ChunkInfo[] = [];
  private width = 0;
  private height = 0;
  private bitDepth = 0;
  private colorType = 0;
  private idatBytes = 0;
  private idatParts: Buffer[] = [];

  constructor(data: Buffer) {
    this.data = data;
  }

  private fail(msg: string): void {
    this.problems.push(msg);
  }

  validate(): ValidationReport {
    const checks: Record<string, boolean> = {};
    const d = this.data;

    checks.signature = d.length >= 8 && d.subarray(0, 8).equals(PNG_SIGNATURE);
    if (!checks.signature) this.fail('bad PNG signature');
    checks.sizeLimit = d.length <= MAX_BYTES;
    if (!checks.sizeLimit) this.fail(`file is ${d.length} bytes, over the 1 MiB limit`);

    // Walk every chunk: [length:4][type:4][data:length][crc:4].
    let off = 8;
    let seenIhdr = false;
    let seenIdat = false;
    let seenIend = false;
    let first = true;
    while (off + 8 <= d.length) {
      const len = readU32BE(d, off);
      const type = d.toString('ascii', off + 4, off + 8);
      const dataStart = off + 8;
      const dataEnd = dataStart + len;
      const crcEnd = dataEnd + 4;
      if (crcEnd > d.length) {
        this.fail(`chunk ${type} at ${off} runs past end of file`);
        break;
      }
      const storedCrc = readU32BE(d, dataEnd);
      const actualCrc = crc32(d, off + 4, dataEnd);
      const crcOk = storedCrc === actualCrc;
      if (!crcOk) this.fail(`chunk ${type} at ${off} has a bad CRC`);
      this.chunks.push({ type, offset: off, length: len, crcOk });

      if (first && type !== 'IHDR') this.fail('first chunk is not IHDR');
      first = false;

      if (type === 'IHDR') {
        seenIhdr = true;
        if (len !== 13) {
          this.fail('IHDR is not 13 bytes');
        } else {
          this.width = readU32BE(d, dataStart);
          this.height = readU32BE(d, dataStart + 4);
          this.bitDepth = d[dataStart + 8];
          this.colorType = d[dataStart + 9];
          const compression = d[dataStart + 10];
          const filter = d[dataStart + 11];
          const interlace = d[dataStart + 12];
          if (compression !== 0) this.fail('IHDR compression method is not 0');
          if (filter !== 0) this.fail('IHDR filter method is not 0');
          if (interlace !== 0 && interlace !== 1) this.fail('IHDR interlace method is invalid');
          if (![0, 2, 3, 4, 6].includes(this.colorType)) this.fail('IHDR colour type is invalid');
          if (![1, 2, 4, 8, 16].includes(this.bitDepth)) this.fail('IHDR bit depth is invalid');
        }
      }
      if (type === 'IDAT') {
        seenIdat = true;
        this.idatBytes += len;
        this.idatParts.push(d.subarray(dataStart, dataEnd));
      }
      if (type === 'IEND') {
        seenIend = true;
        if (len !== 0) this.fail('IEND carries data');
        if (crcEnd !== d.length) {
          this.fail(`trailing ${d.length - crcEnd} bytes after IEND`);
        }
        off = crcEnd;
        break;
      }
      off = crcEnd;
    }

    checks.ihdrFirst = seenIhdr;
    if (!seenIhdr) this.fail('no IHDR chunk');
    checks.hasIdat = seenIdat;
    if (!seenIdat) this.fail('no IDAT chunk');
    checks.iendAtEof = seenIend && off === d.length;
    if (!seenIend) this.fail('no IEND chunk');
    else if (off !== d.length) this.fail('IEND is not the final chunk');
    checks.allCrcOk = this.chunks.every((c) => c.crcOk);
    checks.dimensions = this.width > 0 && this.width <= MAX_DIM &&
      this.height > 0 && this.height <= MAX_DIM;
    if (this.width > 0 && !checks.dimensions) {
      this.fail(`dimensions ${this.width}x${this.height} exceed 1024x1024`);
    }

    // The image data itself must be a well-formed zlib stream, and its
    // inflated size must match what the header describes (one filter byte
    // per scanline plus the pixel bytes).
    let inflatedBytes = 0;
    if (seenIdat && this.idatParts.length > 0) {
      try {
        const raw = inflateSync(Buffer.concat(this.idatParts));
        inflatedBytes = raw.length;
        const bytesPerPixel = this.colorType === 6 ? 4 : this.colorType === 2 ? 3
          : this.colorType === 0 ? 1 : this.colorType === 4 ? 2 : 1;
        const expected = this.height * (1 + Math.ceil((this.width * bytesPerPixel * this.bitDepth) / 8));
        checks.idatInflates = this.bitDepth === 8 ? raw.length === expected : raw.length > 0;
        if (!checks.idatInflates) {
          this.fail(`inflated IDAT is ${raw.length} bytes, expected ${expected}`);
        }
      } catch (err) {
        checks.idatInflates = false;
        this.fail(`IDAT does not inflate: ${(err as Error).message}`);
      }
    } else {
      checks.idatInflates = false;
    }

    checks.valid = this.problems.length === 0;
    return {
      file: 'entry.png',
      bytes: d.length,
      width: this.width,
      height: this.height,
      bitDepth: this.bitDepth,
      colorType: this.colorType,
      chunks: this.chunks,
      idatBytes: this.idatBytes,
      idatInflatedBytes: inflatedBytes,
      checks,
    };
  }

  get ok(): boolean {
    return this.problems.length === 0;
  }

  get errors(): string[] {
    return this.problems;
  }
}

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, 'entry.png');
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const target = join(outDir, 'entry.png');

const bytes = readFileSync(source);
const validator = new PngValidator(bytes);
const report = validator.validate();
console.log(JSON.stringify(report, null, 2));

if (!validator.ok) {
  for (const err of validator.errors) console.error('ERROR:', err);
  process.exit(1);
}

mkdirSync(outDir, { recursive: true });
copyFileSync(source, target);
console.log(`OK: validated ${report.width}x${report.height} PNG (${report.bytes} bytes, `
  + `${report.chunks.length} chunks, all CRCs good) -> ${target}`);
