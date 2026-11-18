// Runs web/translator.js for the Python tests and evaltranslator.py: reads {"direction", "inputs", "options"}
// as JSON on stdin and prints the outputs as a JSON list.
const fs = require("fs");
const path = require("path");
const Translator = require(path.join(__dirname, "..", "..", "web", "translator.js"));

const lexicon = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "..", "src", "thalassian", "data", "lexicon.json"), "utf8"));
const request = JSON.parse(fs.readFileSync(0, "utf8"));
const translate = request.direction === "reverse" ? Translator.reverseTranslate : Translator.strictTranslate;
process.stdout.write(JSON.stringify(request.inputs.map(text => translate(lexicon, text, request.options || {}))));
