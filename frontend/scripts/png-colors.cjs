const fs = require('fs');
const zlib = require('zlib');

const file = process.argv[2];
const buf = fs.readFileSync(file);

if (buf.readUInt32BE(0) !== 0x89504e47) throw new Error('not a png');
let off = 8, width, height, bitDepth, colorType;
const idat = [];

while (off < buf.length) {
  const len = buf.readUInt32BE(off);
  const type = buf.toString('ascii', off + 4, off + 8);
  const data = buf.subarray(off + 8, off + 8 + len);
  if (type === 'IHDR') {
    width = data.readUInt32BE(0);
    height = data.readUInt32BE(4);
    bitDepth = data[8];
    colorType = data[9];
  } else if (type === 'IDAT') {
    idat.push(data);
  } else if (type === 'IEND') break;
  off += 12 + len;
}

console.log(`size: ${width}x${height} bitDepth:${bitDepth} colorType:${colorType}`);
if (bitDepth !== 8 || ![2, 6].includes(colorType)) throw new Error('unsupported format');

const channels = colorType === 6 ? 4 : 3;
const raw = zlib.inflateSync(Buffer.concat(idat));
const stride = width * channels;

const img = Buffer.alloc(height * stride);
let pos = 0;
for (let y = 0; y < height; y++) {
  const filter = raw[pos++];
  for (let x = 0; x < stride; x++) {
    const cur = raw[pos++];
    const left = x >= channels ? img[y * stride + x - channels] : 0;
    const up = y > 0 ? img[(y - 1) * stride + x] : 0;
    const ul = y > 0 && x >= channels ? img[(y - 1) * stride + x - channels] : 0;
    let val;
    if (filter === 0) val = cur;
    else if (filter === 1) val = cur + left;
    else if (filter === 2) val = cur + up;
    else if (filter === 3) val = cur + Math.floor((left + up) / 2);
    else {
      const p = left + up - ul, pa = Math.abs(p - left), pb = Math.abs(p - up), pc = Math.abs(p - ul);
      val = cur + (pa <= pb && pa <= pc ? left : pb <= pc ? up : ul);
    }
    img[y * stride + x] = val & 0xff;
  }
}

function region(x0, y0, x1, y1) {
  const counts = new Map();
  let n = 0;
  for (let y = Math.floor(y0 * height); y < Math.floor(y1 * height); y += 2) {
    for (let x = Math.floor(x0 * width); x < Math.floor(x1 * width); x += 2) {
      const i = y * stride + x * channels;
      const r = img[i], g = img[i + 1], b = img[i + 2];
      const key = `${r >> 3},${g >> 3},${b >> 3}`;
      counts.set(key, (counts.get(key) || 0) + 1);
      n++;
    }
  }
  const top = [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 3)
    .map(([k, c]) => {
      const [r, g, b] = k.split(',').map(v => (v << 3) + 4);
      return `#${[r, g, b].map(v => v.toString(16).padStart(2, '0')).join('')}(${Math.round(c / n * 100)}%)`;
    });
  console.log(`  [${x0}-${x1}, ${y0}-${y1}] ${top.join(' ')}`);
}

console.log('corners & center:');
region(0, 0, 0.2, 0.25);      // top-left
region(0.8, 0, 1, 0.25);      // top-right
region(0, 0.75, 0.2, 1);      // bottom-left
region(0.8, 0.75, 1, 1);      // bottom-right
region(0.35, 0.3, 0.65, 0.55);// center
