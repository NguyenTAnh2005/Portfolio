

export const cutStrDate = (dateISO) =>{
    let dateOnly = dateISO.split('T')[0];
    return dateOnly;
}