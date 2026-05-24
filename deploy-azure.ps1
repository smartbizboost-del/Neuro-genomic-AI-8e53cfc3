# deploy-azure.ps1
# Automates the creation of an Azure Virtual Machine for Neuro-Genomic AI

$ResourceGroup = "NeuroGenomic_RG"
$Location = "eastus"
$VMName = "NeuroGenomicVM"
$AdminUser = "azureuser"

Write-Host "Creating Resource Group..."
az group create --name $ResourceGroup --location $Location

Write-Host "Deploying Virtual Machine..."
# Provisions the VM and pushes the cloud-init YAML which automatically installs Docker
az vm create `
    --resource-group $ResourceGroup `
    --name $VMName `
    --image Ubuntu2204 `
    --admin-username $AdminUser `
    --generate-ssh-keys `
    --custom-data ./azure-cloud-init.yaml `
    --public-ip-sku Standard `
    --size Standard_B2s

Write-Host "Opening Port 80 for NGINX/Dashboard..."
az vm open-port --port 80 --resource-group $ResourceGroup --name $VMName
Write-Host "Opening Port 8000 for API direct access..."
az vm open-port --port 8000 --resource-group $ResourceGroup --name $VMName

Write-Host "Fetching Public IP Address..."
# Print the public IP
az vm list-ip-addresses --resource-group $ResourceGroup --name $VMName --query "[].virtualMachine.network.publicIpAddresses[0].ipAddress" -o tsv

Write-Host "Deployment commanded! Wait approx 3-5 minutes for the cloud-init script to install Docker."
