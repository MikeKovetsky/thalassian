const fs=require('fs');
let lexiconData=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
let CANON=process.argv[3]==='1';
const document={getElementById:(id)=>({checked:CANON})};
function strictTranslate(text) {
            const dropWords = ["для", "в", "до", "на", "з", "за", "від", "про", "і", "та", "але", "for", "to", "the", "a", "an", "and", "of", "in", "on", "with", "by", "but"];
            const pronounSuffixes = {
                "нас": "na", "ми": "anu", "нам": "na", "us": "na", "we": "anu",
                "ти": "a", "тобі": "a", "тебе": "a", "you": "a",
                "я": "o", "мені": "o", "мене": "o", "i": "o", "me": "o",
                "їх": "dan", "вони": "danu", "them": "dan", "they": "danu"
            };

            const tokens = text.match(/[A-Za-zА-Яа-яЄєІіЇїҐґ\']+|[.,!?;]/g) || [];
            let translated = [];
            
            for (let i = 0; i < tokens.length; i++) {
                let word = tokens[i];
                if (/[.,!?;]/.test(word)) {
                    if (translated.length > 0) translated[translated.length-1] += word;
                    continue;
                }

                let lower = word.toLowerCase();
                if (dropWords.includes(lower)) continue;

                let suffix = "";
                if (i + 1 < tokens.length) {
                    let nextWord = tokens[i+1].toLowerCase();
                    if (pronounSuffixes[nextWord]) {
                        suffix = "'" + pronounSuffixes[nextWord];
                        i++; 
                    }
                }

                const canonOnly = document.getElementById('canon-toggle').checked;
                let found = lexiconData.find(e => {
                    if (canonOnly && !e.canon) return false;
                    let uk = e.translation.uk.toLowerCase().split(/[^\wа-яєіїґ\']+/);
                    let en = e.translation.en.toLowerCase().split(/[^\w']+/);
                    return uk.includes(lower) || en.includes(lower) || 
                           (lower.endsWith('и') && uk.includes(lower.slice(0,-1))) ||
                           (lower.endsWith('s') && en.includes(lower.slice(0,-1)));
                });

                if (found) {
                    let elven = found.word;
                    if (translated.length === 0 || (translated.length > 0 && /[.!?;]$/.test(translated[translated.length-1]))) {
                        elven = elven.charAt(0).toUpperCase() + elven.slice(1);
                    }
                    translated.push(elven + suffix);
                } else {
                    translated.push(`[${word}]${suffix}`);
                }
            }

            return translated.join(" ").replace(/ ([.,!?;])/g, "$1");
        }
function reverseTranslate(text) {
            const pronounPrefixes = { "na": "us", "anu": "we", "a": "you", "o": "me", "dan": "them", "danu": "they" };
            
            // Split keeping punctuation
            const tokens = text.match(/[A-Za-z\']+|[.,!?;]/g) || [];
            let translated = [];

            const canonOnly = document.getElementById('canon-toggle').checked;
            
            for (let word of tokens) {
                if (/[.,!?;]/.test(word)) {
                    if (translated.length > 0) translated[translated.length-1] += word;
                    continue;
                }

                let subWords = word.toLowerCase().split("'");
                for (let i=0; i<subWords.length; i++) {
                    let w = subWords[i];
                    if (i > 0 && pronounPrefixes[w]) {
                        translated.push(pronounPrefixes[w]);
                        continue;
                    }

                    let found = lexiconData.find(e => {
                        if (canonOnly && !e.canon) return false;
                        return e.word === w || e.word + "i" === w || e.word.slice(0,-1)+"ei" === w;
                    });
                    if (found) {
                        let t = found.translation.en;
                        if (w.endsWith("i") && found.pos === "noun") t += "(s)";
                        translated.push(t);
                    } else {
                        translated.push(`[${w}]`);
                    }
                }
            }
            return translated.join(" ").replace(/ ([.,!?;])/g, "$1");
        }
const items=[["Alar'annalas", "Ranger Lord"], ["Al diel shala", "Safe travels"], ["Ama noral'arkhana", "Saved by magic"], ["Anar'alah", "By the light"], ["Anar'alah belore", "By the light of the sun"], ["Anaria shola", "Speak your business"], ["Anar'endal dracon", "By the breath of the dragon"], ["Ann'da", "Father"], ["Anu belore dela'na", "The sun guides us"], ["Aranal", "Rise"], ["Bal'a dash malanore", "Greetings traveler"], ["Ban'dinoriel", "Gate keeper"], ["Bash'a no falor talah", "Taste the chill of true death"], ["Belono sil'aru belore'dorei", "Shoulder your burdens well child of the sun"], ["Belore", "The sun"], ["Belore'dorei", "Child of the sun"], ["Doral ana'diel", "How fare you"], ["Elor bindel felallan morin'aminor", "Sleep forever in quiet serenity"], ["Elu'meniel mal alann", "May peace calm your heart"], ["Felo'melorn", "Flame strike"], ["Kim'jael", "Little rat"], ["Medivh", "Keeper of secrets"], ["Minn'da", "Mother"], ["Quel'dorei", "Children of noble birth"], ["Quel'Thalas", "High home"], ["Rea", "And"], ["Ren'dorei", "Children of the void"], ["Selama ashal'anore", "Justice for our people"], ["Shal'na", "Aunt"], ["Shindu fallah na", "They are breaking through"], ["Shindu fallah na", "Our enemies are breaking through"], ["Shindu sin'dorei", "Failing children of the blood"], ["Shorel'aran", "Farewell"], ["Sin'dorei", "Children of the blood"], ["Sinu a'manore", "Well met"], ["Tal anu'men no Sin'dorei", "Death to all who oppose the children of the blood"], ["Thas'alah", "Light of the forest"], ["Thas'dorah", "Valor of the forest"], ["Vendel'o eranu", "Help me forget"]];
console.log(JSON.stringify(items.map(([ph,gl])=>[ph,gl,strictTranslate(gl),reverseTranslate(ph)])));
