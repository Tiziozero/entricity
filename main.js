const fetchIndex = async () => {
    try {
        const data = fetch(url);
        if (data.ok) {
            const json = JSON.parse(data.body);
            return json;
        } else {
            // handle error
        }
        console.log(data)
    } catch (e) {
        console.error(e)
    }
}
const parsedJson = await fetchIndex("data.json");
console.log(parsedJson)
