curl http://localhost:11434/api/generate -d '{
  "model": "codellama:7b-instruct",
  "prompt": "Écris une fonction Python qui trie une liste",
  "stream": false
}'
