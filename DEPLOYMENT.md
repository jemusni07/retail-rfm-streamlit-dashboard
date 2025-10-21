# Deployment Guide for RFM Streamlit Dashboard

This guide provides step-by-step instructions for deploying your RFM Customer Segmentation Dashboard to various cloud platforms.

## Prerequisites

1. **Environment Variables**: Ensure you have your Databricks credentials ready:
   - `DATABRICKS_SERVER_HOSTNAME`
   - `DATABRICKS_WAREHOUSE_ID` or `DATABRICKS_HTTP_PATH`
   - `DATABRICKS_ACCESS_TOKEN`
   - `DATABASE_NAME`
   - `TABLE_NAME`

2. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, etc.)

## Deployment Options

### Option 1: Streamlit Community Cloud (Recommended for Streamlit Apps)

**Pros**: Free, designed specifically for Streamlit, easy setup
**Cons**: Limited to Streamlit apps only

#### Steps:
1. **Push to GitHub**: Ensure your code is in a GitHub repository
2. **Visit Streamlit Cloud**: Go to [share.streamlit.io](https://share.streamlit.io)
3. **Sign in**: Use your GitHub account
4. **Deploy**:
   - Click "New app"
   - Select your repository
   - Choose the branch (usually `main`)
   - Set the main file path to `main.py`
   - Add environment variables in the "Advanced settings"
5. **Environment Variables**: Add all your Databricks credentials:
   ```
   DATABRICKS_SERVER_HOSTNAME=your-workspace.cloud.databricks.com
   DATABRICKS_WAREHOUSE_ID=your-warehouse-id
   DATABRICKS_ACCESS_TOKEN=your-access-token
   DATABASE_NAME=retail_analytics
   TABLE_NAME=dlt.segment_summary
   ```

### Option 2: Railway (Great for Python Apps)

**Pros**: Simple deployment, good for Python apps, reasonable pricing
**Cons**: Requires Docker setup

#### Steps:
1. **Sign up**: Go to [railway.app](https://railway.app) and sign up
2. **Create Project**: Click "New Project"
3. **Deploy from GitHub**: Select your repository
4. **Configure**:
   - Railway will auto-detect it's a Python app
   - It will use the Dockerfile we created
5. **Environment Variables**: Add your Databricks credentials in the Railway dashboard
6. **Deploy**: Railway will automatically build and deploy your app

### Option 3: Render (Developer-Friendly)

**Pros**: Free tier available, good documentation
**Cons**: Free tier has limitations

#### Steps:
1. **Sign up**: Go to [render.com](https://render.com) and sign up
2. **Create Web Service**: Click "New" → "Web Service"
3. **Connect Repository**: Connect your GitHub repository
4. **Configure**:
   - Name: `rfm-dashboard`
   - Environment: `Docker`
   - Dockerfile Path: `Dockerfile`
   - Port: `8501`
5. **Environment Variables**: Add your Databricks credentials
6. **Deploy**: Click "Create Web Service"

### Option 4: Heroku (Classic Choice)

**Pros**: Well-documented, reliable
**Cons**: No free tier, requires credit card

#### Steps:
1. **Install Heroku CLI**: Download from [devcenter.heroku.com](https://devcenter.heroku.com)
2. **Login**: `heroku login`
3. **Create App**: `heroku create your-app-name`
4. **Set Environment Variables**:
   ```bash
   heroku config:set DATABRICKS_SERVER_HOSTNAME=your-workspace.cloud.databricks.com
   heroku config:set DATABRICKS_WAREHOUSE_ID=your-warehouse-id
   heroku config:set DATABRICKS_ACCESS_TOKEN=your-access-token
   heroku config:set DATABRICKS_DATABASE_NAME=retail_analytics
   heroku config:set TABLE_NAME=dlt.segment_summary
   ```
5. **Deploy**: `git push heroku main`

### Option 5: AWS EC2 (Full Control)

**Pros**: Full control, can handle high traffic
**Cons**: More complex setup, requires AWS knowledge

#### Steps:
1. **Launch EC2 Instance**: Use Ubuntu 22.04 LTS
2. **Install Docker**: Follow Docker installation guide
3. **Clone Repository**: `git clone your-repo-url`
4. **Set Environment Variables**: Create `.env` file with your credentials
5. **Run with Docker**: `docker run -d -p 8501:8501 --env-file .env your-app`

## Security Considerations

### Environment Variables
- **Never commit** your `.env` file to Git
- Use platform-specific environment variable settings
- Consider using secret management services for production

### Databricks Security
- Use service accounts with minimal required permissions
- Regularly rotate access tokens
- Consider using Databricks Unity Catalog for enhanced security

## Troubleshooting

### Common Issues:

1. **Connection Timeout**: Check your Databricks server hostname and network connectivity
2. **Authentication Failed**: Verify your access token and permissions
3. **Data Not Loading**: Check database and table names
4. **App Crashes**: Check logs for specific error messages

### Debugging Steps:
1. Test locally with `streamlit run main.py`
2. Check environment variables are set correctly
3. Verify Databricks connectivity
4. Review platform-specific logs

## Performance Optimization

### For Production:
1. **Caching**: The app already uses `@st.cache_data(ttl=300)` for 5-minute caching
2. **Connection Pooling**: Consider implementing connection pooling for high traffic
3. **Monitoring**: Set up monitoring and alerting for your deployment platform
4. **Scaling**: Configure auto-scaling based on traffic patterns

## Cost Estimation

- **Streamlit Community Cloud**: Free
- **Railway**: $5/month for hobby plan
- **Render**: Free tier available, $7/month for starter plan
- **Heroku**: $7/month for basic plan
- **AWS EC2**: $5-20/month depending on instance size

## Recommended Approach

For most use cases, I recommend starting with **Streamlit Community Cloud** because:
- It's free
- Designed specifically for Streamlit apps
- Easy setup and management
- Automatic deployments from GitHub

If you need more control or have specific requirements, consider **Railway** or **Render** as excellent alternatives.

## Next Steps

1. Choose your deployment platform
2. Set up your environment variables
3. Deploy your application
4. Test the deployed application
5. Set up monitoring and alerts (optional)

Your dashboard should be accessible via the provided URL after successful deployment!
