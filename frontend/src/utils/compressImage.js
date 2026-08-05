/* Shrink an image in the browser before it is uploaded.
 *
 * A photo straight off a phone is several megabytes of pixels nothing in this app
 * ever displays: the largest place a product image appears is a detail header a
 * few hundred pixels wide. Sending the original means a slow upload, a large file
 * kept forever, and a slow page for every user who later views it.
 *
 * So the image is drawn into a canvas at a sane maximum size and re-encoded. What
 * comes back is a File, so callers upload it exactly as they uploaded the original.
 *
 * Left alone deliberately:
 *  - GIFs, because a canvas keeps only the first frame and would silently destroy
 *    an animation.
 *  - Anything that is already smaller than the threshold, since re-encoding a small
 *    image usually makes it larger, not smaller.
 *  - Anything the browser cannot decode; the original is returned and the upload
 *    proceeds as it did before.
 */

const DEFAULTS = {
  // Comfortably above the largest size any view renders, so shrinking is never
  // visible as blur.
  maxDimension: 1600,
  quality: 0.82,
  // Below this, re-encoding costs more bytes than it saves.
  skipUnderBytes: 200 * 1024,
  // Formats a canvas can safely re-encode without losing something.
  encodable: ["image/png", "image/jpeg", "image/jpg", "image/webp"],
};

function loadImage(file) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const image = new Image();
    image.onload = () => { URL.revokeObjectURL(url); resolve(image); };
    image.onerror = () => { URL.revokeObjectURL(url); reject(new Error("decode failed")); };
    image.src = url;
  });
}

function toBlob(canvas, type, quality) {
  return new Promise((resolve) => { canvas.toBlob(resolve, type, quality); });
}

function renamed(name, type) {
  const stem = name.replace(/\.[^.]+$/, "") || "image";
  const extension = type === "image/webp" ? "webp" : "jpg";
  return `${stem}.${extension}`;
}

export async function compressImage(file, options = {}) {
  const settings = { ...DEFAULTS, ...options };
  if (!file || !settings.encodable.includes(file.type)) return file;
  if (file.size <= settings.skipUnderBytes) return file;
  if (typeof document === "undefined" || typeof URL.createObjectURL !== "function") return file;

  let image;
  try {
    image = await loadImage(file);
  } catch {
    return file;
  }

  const longest = Math.max(image.naturalWidth, image.naturalHeight);
  const scale = longest > settings.maxDimension ? settings.maxDimension / longest : 1;
  const width = Math.max(1, Math.round(image.naturalWidth * scale));
  const height = Math.max(1, Math.round(image.naturalHeight * scale));

  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const context = canvas.getContext("2d");
  if (!context) return file;
  // A PNG with transparency re-encoded as JPEG would show black where it was
  // clear, so the canvas starts white and the result reads as it looked.
  context.fillStyle = "#fff";
  context.fillRect(0, 0, width, height);
  context.drawImage(image, 0, 0, width, height);

  // WebP where the browser can produce it, JPEG otherwise. `toBlob` falls back to
  // PNG for a type it does not support, which would be larger than the original,
  // so the result's own type is what decides whether it is kept.
  let blob = await toBlob(canvas, "image/webp", settings.quality);
  if (!blob || blob.type !== "image/webp") {
    blob = await toBlob(canvas, "image/jpeg", settings.quality);
  }
  if (!blob || blob.size >= file.size) return file;

  return new File([blob], renamed(file.name, blob.type), {
    type: blob.type,
    lastModified: Date.now(),
  });
}

export default compressImage;
