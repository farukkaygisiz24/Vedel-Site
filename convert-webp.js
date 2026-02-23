const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const publicDir = path.join(__dirname, 'public');

// Büyük resimleri kontrol et
const largeImages = [
  'sakura.jpg',
  'MHI/plusk.jpg',
  'MHI/kaset-b.jpg',
  'euroform/dış motor küçük.jpg',
  'MHI/plusb.jpg',
  'MHI/diamondg.jpg',
  'euroform/dış motor büyük.jpg'
];

async function convertToWebP(inputPath) {
  const dir = path.dirname(inputPath);
  const filename = path.basename(inputPath, path.extname(inputPath));
  const outputPath = path.join(dir, `${filename}.webp`);
  
  try {
    await sharp(inputPath)
      .resize(1200, null, { withoutEnlargement: true })
      .webp({ quality: 80 })
      .toFile(outputPath);
    
    const originalSize = fs.statSync(inputPath).size;
    const webpSize = fs.statSync(outputPath).size;
    const savings = ((originalSize - webpSize) / originalSize * 100).toFixed(1);
    
    console.log(`✅ ${filename}: ${(originalSize/1024).toFixed(0)}KB → ${(webpSize/1024).toFixed(0)}KB (${savings}% tasarruf)`);
  } catch (err) {
    console.log(`❌ ${inputPath}: ${err.message}`);
  }
}

console.log('🔄 Resimler WebP\'ye dönüştürülüyor...\n');

(async () => {
  for (const img of largeImages) {
    const fullPath = path.join(publicDir, img);
    if (fs.existsSync(fullPath)) {
      await convertToWebP(fullPath);
    } else {
      console.log(`❌ Bulunamadı: ${img}`);
    }
  }
  console.log('\n✅ İşlem tamamlandı!');
})();
