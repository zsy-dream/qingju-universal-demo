const fs = require('fs');
const path = require('path');

function processDir(dir) {
    const files = fs.readdirSync(dir);
    for (const f of files) {
        const p = path.join(dir, f);
        if (fs.statSync(p).isDirectory()) {
            processDir(p);
        } else if (p.endsWith('.vue')) {
            let content = fs.readFileSync(p, 'utf8');

            let newContent = content
                .replace(/bg-black\/\d+/g, 'bg-white')
                .replace(/bg-white\/5/g, 'bg-slate-50')
                .replace(/bg-white\/10/g, 'bg-slate-50')
                .replace(/bg-white\/20/g, 'bg-white')
                .replace(/border-white\/\d+/g, 'border-slate-100')

                .replace(/text-white\/95/g, 'text-slate-900')
                .replace(/text-white\/80/g, 'text-slate-800')
                .replace(/text-white\/70/g, 'text-slate-600')
                .replace(/text-white\/60/g, 'text-slate-500')
                .replace(/text-white\/50/g, 'text-slate-400')
                .replace(/text-slate-100/g, 'text-slate-900')

                .replace(/text-brandPrimary/g, 'text-lime-600')
                .replace(/bg-brandPrimary/g, 'bg-lime-500')
                .replace(/accent-brandPrimary/g, 'accent-lime-500')
                .replace(/text-brandSecondary/g, 'text-sky-500')
                .replace(/bg-brandSecondary/g, 'bg-sky-500')
                .replace(/text-brandAccent/g, 'text-lime-500')

                .replace(/color:\s*'#3B82F6'/g, "color: '#84cc16'")
                .replace(/color:\s*'#22D3EE'/g, "color: '#38bdf8'")
                .replace(/color:\s*'#EC4899'/g, "color: '#0ea5e9'")
                .replace(/rgba\(255,\s*255,\s*255,\s*0\.08\)/g, "'rgba(0,0,0,0.04)'")
                .replace(/rgba\(255,\s*255,\s*255,\s*0\.5\)/g, "'rgba(0,0,0,0.45)'")
                .replace(/rgba\(255,\s*255,\s*255,\s*0\.6\)/g, "'rgba(0,0,0,0.6)'")

                .replace(/shadow-youthful/g, 'shadow-btn');

            if (content !== newContent) {
                fs.writeFileSync(p, newContent);
                console.log('Processed ' + p);
            }
        }
    }
}

processDir('d:/互联网+项目开发/11 青居智算——基于Hedonic模型的高校毕业生租房防坑与真实估值系统/Universal_System/frontend/src');
console.log('Batch theme update complete.');
