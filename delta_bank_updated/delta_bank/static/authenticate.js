const message = document.getElementById('result');

async function get_code() {

    const user_id = document.getElementById("user_id").value;
    const email = document.getElementById("email").value;

    const form = document.getElementById('otp_form');
    const formData = new FormData(form);
    formData.append("user_id", user_id)
    formData.append("email", email)

    try{
        //Tjek om credit acc findes
        const otp_response = await fetch("http://localhost:8100/api/auth/otp/generate", {
            method: 'POST',
            body: formData
        })

        const otp_data = await otp_response.json()
        console.log(otp_data)
        
        message.innerText = "Din kode til authentication er: \n" + otp_data.base32;
        return;

    } catch (error) {
        console.log('Error:', error);
    }
}

async function verify_code() {

    const user_id = document.getElementById("user_id").value;
    const token = document.getElementById("token").value;

    const form = document.getElementById('otp_form');
    const formData = new FormData(form);
    formData.append("user_id", user_id)
    formData.append("token", token)

    try{
        //Tjek om credit acc findes
        const otp_response = await fetch("http://localhost:8100/api/auth/otp/verify", {
            method: 'POST',
            body: formData
        })

        const otp_data = await otp_response.json()
        console.log(otp_data)
        if(otp_data.otp_verified){
            window.location.href = "/";
        } else {
            message.innerText = "noget gik galt";
            return;
        }
 

    } catch (error) {
        console.log('Error:', error);
    }
}

