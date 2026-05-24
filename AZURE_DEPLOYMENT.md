# Azure Deployment Guide

Deploy the Neuro-Genomic AI backend to Azure for Streamlit Cloud integration.

## Prerequisites

1. **Azure Account** - Create one at https://azure.microsoft.com/free/
2. **Azure CLI** - Install from https://learn.microsoft.com/cli/azure/install-azure-cli
3. **PowerShell 7+** - Install from https://learn.microsoft.com/powershell/scripting/install/installing-powershell
4. **Git** - Ensure code is pushed to https://github.com/ibrahim2002-dev/Neurogenomic2

## Step 1: Login to Azure

```powershell
az login
```

This opens a browser for authentication. Complete the login flow.

## Step 2: Run the Deployment Script

Execute the PowerShell deployment script (adjust resource group name if needed):

```powershell
cd "c:\Users\ibrah\Downloads\Neuro-genomic-AI-8e53cfc3-main\Neuro-genomic-AI-8e53cfc3-main"
.\deploy-azure.ps1
```

**What this does:**
- Creates a resource group `NeuroGenomic_RG` in East US
- Provisions an Ubuntu VM with Docker pre-installed
- Clones your GitHub repository
- Starts all services (API, Dashboard, Database, Redis, MinIO)
- Opens ports 80 and 8000 for access

**Expected time:** 3-5 minutes

## Step 3: Get the Public IP

After deployment completes, you'll see output like:

```
Public IP Address: 20.123.456.789
```

Save this IP. If you miss it, retrieve it with:

```powershell
az vm list-ip-addresses --resource-group NeuroGenomic_RG --name NeuroGenomicVM --query "[].virtualMachine.network.publicIpAddresses[0].ipAddress" -o tsv
```

## Step 4: Verify the Backend is Running

Wait 2-3 minutes for cloud-init to complete, then test:

```
http://20.123.456.789:8000/health
```

Should return:
```json
{"status": "healthy", "timestamp": "2026-05-24T..."}
```

If it fails, check logs on the VM:
```powershell
az vm run-command invoke --resource-group NeuroGenomic_RG --name NeuroGenomicVM --command-id RunShellScript --scripts "docker compose -f /opt/neuro-genomic-ai/docker-compose.yml ps"
```

## Step 5: Configure Streamlit Cloud

1. Go to https://share.streamlit.io → Your apps
2. Find **Neuro-Genomic AI**
3. Click the menu (⋮) → Settings
4. Under **Secrets**, add:

```
API_URL=http://20.123.456.789:8000
```

(Replace the IP with your actual public IP)

5. Click **Save** and refresh your Streamlit app

## Step 6: Test Upload

1. Go to https://neurogenomic2.streamlit.app
2. Login or sign up
3. Upload a fetal ECG file
4. Verify the upload succeeds (no "Connection refused" error)

## Troubleshooting

### "Connection refused" on Streamlit Cloud
- Verify the IP in `API_URL` is correct
- Check the Azure VM is running: `az vm get-instance-view --resource-group NeuroGenomic_RG --name NeuroGenomicVM --query "powerState"`
- Verify port 8000 is open: `az vm open-port --port 8000 --resource-group NeuroGenomic_RG --name NeuroGenomicVM`

### Docker services not starting
SSH into the VM and check logs:
```bash
ssh azureuser@20.123.456.789
cd /opt/neuro-genomic-ai
docker compose logs api
```

### Need to redeploy
Clean up the old deployment:
```powershell
az group delete --name NeuroGenomic_RG --yes
```

Then run the deployment script again.

## Cost Estimation

- **VM (Standard_B2s):** ~$50/month
- **Data egress:** Varies (typically <$1/month for low traffic)
- **Storage:** Minimal (~$1/month for managed disks)

**Total:** ~$50-60/month

To minimize costs:
- Stop the VM when not in use: `az vm deallocate --resource-group NeuroGenomic_RG --name NeuroGenomicVM`
- Start when needed: `az vm start --resource-group NeuroGenomic_RG --name NeuroGenomicVM`

## Next Steps

- Monitor logs: `docker compose logs -f api`
- Update code: Push to GitHub, then SSH and `git pull && docker compose up -d --build`
- Scale up if needed: Resize the VM via Azure Portal
