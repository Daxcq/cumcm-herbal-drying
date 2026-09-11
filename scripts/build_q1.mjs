import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

// 获取当前文件所在目录
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = join(__dirname, "..");

const inputPath = join(projectRoot, "data/raw/附件1.xlsx");
const templatePath = join(projectRoot, "data/raw/附件3/result1.xlsx");
const outputDir = join(projectRoot, "outputs/q1");
const outputPath = join(outputDir, "result1.xlsx");

const srcBook = await SpreadsheetFile.importXlsx(await FileBlob.load(inputPath));
const src = srcBook.worksheets.getItemAt(0).getUsedRange().values;
const env = src.slice(1).filter(row => Number.isFinite(Number(row[0]))).map(row => [Number(row[0]), Number(row[1]), Number(row[2])]);
const tSrc = env.map(row => row[0]);
const taSrc = env.map(row => row[1]);
const caSrc = env.map(row => row[2]);

const dt = 1;
const n = 20;
const dr = 0.02 / n;
const r = Array.from({ length: n + 1 }, (_, j) => j * dr);
const rho = 820;
const cp = 2600;
const k = 0.36;
const hT = 25;
const hm = 8e-7;
const alpha = k / (rho * cp);

function interp(x, xs, ys) {
  if (x <= xs[0]) return ys[0];
  if (x >= xs[xs.length - 1]) return ys[ys.length - 1];
  let lo = 0, hi = xs.length - 1;
  while (hi - lo > 1) {
    const mid = Math.floor((lo + hi) / 2);
    if (xs[mid] <= x) lo = mid; else hi = mid;
  }
  const w = (x - xs[lo]) / (xs[hi] - xs[lo]);
  return ys[lo] + w * (ys[hi] - ys[lo]);
}

const ta = Array.from({ length: 1801 }, (_, t) => interp(t, tSrc, taSrc));
const ca = Array.from({ length: 1801 }, (_, t) => interp(t, tSrc, caSrc));

function solveLinear(aIn, bIn) {
  const a = aIn.map(row => row.slice());
  const b = bIn.slice();
  const m = b.length;
  for (let col = 0; col < m; col++) {
    let pivot = col;
    for (let row = col + 1; row < m; row++) if (Math.abs(a[row][col]) > Math.abs(a[pivot][col])) pivot = row;
    [a[col], a[pivot]] = [a[pivot], a[col]];
    [b[col], b[pivot]] = [b[pivot], b[col]];
    const p = a[col][col];
    for (let j = col; j < m; j++) a[col][j] /= p;
    b[col] /= p;
    for (let row = 0; row < m; row++) {
      if (row === col) continue;
      const f = a[row][col];
      if (f === 0) continue;
      for (let j = col; j < m; j++) a[row][j] -= f * a[col][j];
      b[row] -= f * b[col];
    }
  }
  return b;
}

function buildOperator(d, boundaryCoeff) {
  const diffusivity = Array.isArray(d) ? d : Array(n + 1).fill(d);
  const M = Array.from({ length: n + 1 }, () => Array(n + 1).fill(0));
  const q = Array(n + 1).fill(0);
  const d0 = (diffusivity[0] + diffusivity[1]) / 2;
  M[0][0] = -4 * d0 / dr ** 2;
  M[0][1] = 4 * d0 / dr ** 2;
  for (let j = 1; j < n; j++) {
    const dL = (diffusivity[j - 1] + diffusivity[j]) / 2;
    const dR = (diffusivity[j] + diffusivity[j + 1]) / 2;
    const rL = r[j] - dr / 2;
    const rR = r[j] + dr / 2;
    M[j][j - 1] = rL * dL / (r[j] * dr ** 2);
    M[j][j] = -(rR * dR + rL * dL) / (r[j] * dr ** 2);
    M[j][j + 1] = rR * dR / (r[j] * dr ** 2);
  }
  const dL = (diffusivity[n - 1] + diffusivity[n]) / 2;
  const rL = r[n] - dr / 2;
  M[n][n - 1] = rL * dL / (r[n] * dr ** 2);
  M[n][n] = -rL * dL / (r[n] * dr ** 2) - boundaryCoeff / dr;
  q[n] = boundaryCoeff / dr;
  return { M, q };
}

function step(old, diffusivity, boundaryCoeff, ambient) {
  const { M, q } = buildOperator(diffusivity, boundaryCoeff);
  const A = M.map((row, i) => row.map((v, j) => (i === j ? 1 : 0) - dt * v));
  const b = old.map((v, i) => v + dt * q[i] * ambient);
  return solveLinear(A, b);
}

const temp = Array.from({ length: 1801 }, () => Array(n + 1).fill(0));
let T = Array(n + 1).fill(28);
temp[0] = T.slice();
for (let t = 1; t <= 1800; t++) {
  T = step(T, alpha, hT / k, ta[t]);
  temp[t] = T.slice();
}

const moisture = Array.from({ length: 1801 }, () => Array(n + 1).fill(0));
let C = Array(n + 1).fill(2.55);
moisture[0] = C.slice();
for (let t = 1; t <= 1800; t++) {
  let guess = C.slice();
  for (let iter = 0; iter < 100; iter++) {
    const D = guess.map(x => 7e-9 * Math.exp(-0.89 * x));
    const next = step(C, D, hm, ca[t]);
    const err = Math.max(...next.map((x, j) => Math.abs(x - guess[j])));
    guess = guess.map((x, j) => 0.5 * x + 0.5 * next[j]);
    if (err < 1e-10) { guess = next; break; }
  }
  C = guess;
  moisture[t] = C.slice();
}

const outBook = await SpreadsheetFile.importXlsx(await FileBlob.load(templatePath));
const headers = ["时间\\到药材中心的距离", ...Array.from({ length: n + 1 }, (_, j) => +(j * 0.1).toFixed(1))];
const rows = (field) => Array.from({ length: 1800 }, (_, i) => [i + 1, ...field[i + 1].map(x => +x.toFixed(4))]);
for (const [sheetIndex, field] of [[0, temp], [1, moisture]]) {
  const sheet = outBook.worksheets.getItemAt(sheetIndex);
  sheet.getRange("A1:V1801").clear({ applyTo: "contents" });
  sheet.getRange("A1:V1801").values = [headers, ...rows(field)];
  sheet.getRange("A1:V1801").format.numberFormat = "0.0000";
  sheet.getRange("A1").format.numberFormat = "@";
  sheet.getRange("B1:V1").format.numberFormat = "0.0";
  sheet.getRange("A1:V1801").format.autofitColumns();
}

await fs.mkdir(outputDir, { recursive: true });
const output = await SpreadsheetFile.exportXlsx(outBook);
await output.save(outputPath);
console.log(JSON.stringify({ outputPath, alpha, temp100: temp[100], temp1800: temp[1800], moisture100: moisture[100], moisture1800: moisture[1800] }));
