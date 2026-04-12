/**
 * Feishu Channel Setup Tools
 * 飞书 Channel 配置工具
 */

const FEISHU_API_BASE = 'https://open.feishu.cn/open-apis';

/**
 * 获取 Access Token
 */
async function getTenantAccessToken(appId, appSecret) {
  const response = await fetch(`${FEISHU_API_BASE}/auth/v3/tenant_access_token/internal`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      app_id: appId,
      app_secret: appSecret
    })
  });
  
  const result = await response.json();
  if (result.code !== 0) {
    throw new Error(`获取 Token 失败: ${result.msg}`);
  }
  return result.tenant_access_token;
}

/**
 * 发送消息
 */
async function sendMessage(accessToken, receiveId, receiveIdType, content, msgType = 'text') {
  const response = await fetch(`${FEISHU_API_BASE}/im/v1/messages?receive_id_type=${receiveIdType}`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      receive_id: receiveId,
      msg_type: msgType,
      content: JSON.stringify(msgType === 'text' ? { text: content } : content)
    })
  });
  
  const result = await response.json();
  if (result.code !== 0) {
    throw new Error(`发送消息失败: ${result.msg}`);
  }
  return result.data;
}

/**
 * 获取用户信息
 */
async function getUserInfo(accessToken, userId, userIdType = 'open_id') {
  const response = await fetch(`${FEISHU_API_BASE}/contact/v3/users/${userId}?user_id_type=${userIdType}`, {
    headers: { 'Authorization': `Bearer ${accessToken}` }
  });
  
  const result = await response.json();
  if (result.code !== 0) {
    throw new Error(`获取用户信息失败: ${result.msg}`);
  }
  return result.data.user;
}

/**
 * 获取群聊列表
 */
async function getChatList(accessToken, pageSize = 20) {
  const response = await fetch(`${FEISHU_API_BASE}/im/v1/chats?page_size=${pageSize}`, {
    headers: { 'Authorization': `Bearer ${accessToken}` }
  });
  
  const result = await response.json();
  if (result.code !== 0) {
    throw new Error(`获取群聊列表失败: ${result.msg}`);
  }
  return result.data.items || [];
}

/**
 * 验证权限配置
 */
async function verifyPermissions(appId, appSecret) {
  const token = await getTenantAccessToken(appId, appSecret);
  
  // 尝试调用需要权限的 API 来验证
  try {
    await getChatList(token, 1);
    return { success: true, message: '权限配置正确' };
  } catch (error) {
    return { success: false, message: error.message };
  }
}

// ============================================
// 工具定义
// ============================================

module.exports = {
  tools: {
    /**
     * 配置飞书 Channel
     */
    feishu_setup_channel: {
      description: '配置飞书 Channel，需要提供 App ID 和 App Secret',
      parameters: {
        type: 'object',
        properties: {
          appId: {
            type: 'string',
            description: '飞书应用的 App ID（格式：cli_xxx）'
          },
          appSecret: {
            type: 'string',
            description: '飞书应用的 App Secret'
          }
        },
        required: ['appId', 'appSecret']
      },
      handler: async (params) => {
        const { appId, appSecret } = params;
        
        // 验证凭证
        const verifyResult = await verifyPermissions(appId, appSecret);
        if (!verifyResult.success) {
          return { success: false, error: verifyResult.message };
        }
        
        // 返回配置指引
        return {
          success: true,
          message: '凭证验证成功，请按以下步骤完成配置：\n1. 编辑 ~/.openclaw/openclaw.json\n2. 添加飞书 channel 配置\n3. 运行 openclaw gateway restart',
          config: {
            channels: {
              feishu: {
                appId: appId,
                appSecret: appSecret,
                enabled: true
              }
            }
          }
        };
      }
    },
    
    /**
     * 发送飞书消息
     */
    feishu_send_message: {
      description: '通过飞书发送消息',
      parameters: {
        type: 'object',
        properties: {
          appId: { type: 'string', description: '飞书 App ID' },
          appSecret: { type: 'string', description: '飞书 App Secret' },
          receiveId: { type: 'string', description: '接收者 ID（open_id/user_id/union_id/email/chat_id）' },
          receiveIdType: { 
            type: 'string', 
            description: 'ID 类型',
            enum: ['open_id', 'user_id', 'union_id', 'email', 'chat_id'],
            default: 'open_id'
          },
          message: { type: 'string', description: '消息内容' }
        },
        required: ['appId', 'appSecret', 'receiveId', 'message']
      },
      handler: async (params) => {
        const { appId, appSecret, receiveId, receiveIdType, message } = params;
        
        const token = await getTenantAccessToken(appId, appSecret);
        const result = await sendMessage(token, receiveId, receiveIdType, message);
        
        return { success: true, messageId: result.message_id };
      }
    },
    
    /**
     * 验证飞书配置
     */
    feishu_verify_config: {
      description: '验证飞书 Channel 配置是否正确',
      parameters: {
        type: 'object',
        properties: {
          appId: { type: 'string', description: '飞书 App ID' },
          appSecret: { type: 'string', description: '飞书 App Secret' }
        },
        required: ['appId', 'appSecret']
      },
      handler: async (params) => {
        const { appId, appSecret } = params;
        return await verifyPermissions(appId, appSecret);
      }
    }
  }
};
