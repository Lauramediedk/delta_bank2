//Liste over hvilke API de forkskellige banker har
//De 4 første cifre i kontonr. fortæller hvilken bank det hørertil
const bank_urls = {
    '8075': 'http://localhost:8100/',  //delta bank    
    '2040': 'http://localhost:8200/'   //danske bank
};


async function make_transfer() {

    //Få url til bank hvor penge fratrækkes
    const debit_account = document.getElementById("id_debit_account").value;
    console.log("debit: "+ debit_account)
    const from_bank = debit_account.slice(0, 4);
    const from_bank_url = bank_urls[from_bank]

    //Få url til bank hvor penge indsættes
    const credit_account = document.getElementById("id_credit_account").value;
    const to_bank = credit_account.slice(0, 4);
    const to_bank_url = bank_urls[to_bank]

    //Omdan djangoform til Formdata
    const form = document.getElementById('transfer_form');
    const formData = new FormData(form);

    try{
        //Tjek om credit acc findes
        const credit_acc_response = await fetch(to_bank_url + "api/v1/credit_acc_validation/", {
            method: 'POST',
            body: formData
        })
        if (credit_acc_response.ok) {
            console.log("credit fundet")
        } else {
            console.log("credit ikke fundet")
            return
        }
        const credit_acc_data = await credit_acc_response.json()
        
        //Fratræk penge fra afsenders konto
        const transfer_from_response = await fetch(from_bank_url + "api/v1/make_transfer/from/", {
            method: 'POST',
            body: formData
        })
        if (transfer_from_response.ok) {
            console.log("transfer from request ok")
        } else {
            console.log("transfer from request error")
            
        }
        const from_data = await transfer_from_response.json()
        const unique_id = from_data.unique_id
        console.log("unique_id: " + unique_id) 

        //tilføj penge til modtagers konto
        formData.append('unique_id',from_data.unique_id)
        const transfer_to_response = await fetch(to_bank_url + "api/v1/make_transfer/to/", {
            method: 'POST',
            body: formData
        })
        if (transfer_to_response.ok) {
            console.log("transfer to request ok")
        } else {
            console.log("transfer to request error")
        }

    } catch (error) {
        console.log('Error:', error);
    }
}

