export const pushAfterFieldName = (json, fieldname, data) => {
    const index = json.findIndex(field => field.fieldname === fieldname);
    if (index !== -1) {
        json.splice(index + 1, 0, data);
    } else {
        json.push(data);
    }

    return json;
}