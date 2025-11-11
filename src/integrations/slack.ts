import { IncomingWebhook } from '@slack/webhook';
import { SlackConfig, SlackMessage, IntegrationResponse } from '../types';

export class SlackIntegration {
  private config: SlackConfig;
  private webhook: IncomingWebhook;

  constructor(config: SlackConfig) {
    this.config = config;
    this.webhook = new IncomingWebhook(config.webhookUrl);
  }

  /**
   * Send a message to Slack
   */
  async sendMessage(message: SlackMessage): Promise<IntegrationResponse> {
    try {
      const payload: any = {
        text: message.text,
        channel: message.channel || this.config.channel,
      };

      if (message.username) {
        payload.username = message.username;
      }

      if (message.iconEmoji) {
        payload.icon_emoji = message.iconEmoji;
      }

      if (message.attachments && message.attachments.length > 0) {
        payload.attachments = message.attachments.map((attachment) => ({
          color: attachment.color,
          title: attachment.title,
          text: attachment.text,
          fields: attachment.fields,
        }));
      }

      await this.webhook.send(payload);

      return {
        success: true,
        data: { message: 'Message sent successfully' },
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message,
      };
    }
  }

  /**
   * Send a simple text message
   */
  async sendSimpleMessage(text: string, channel?: string): Promise<IntegrationResponse> {
    return this.sendMessage({
      text,
      channel: channel || this.config.channel,
    });
  }

  /**
   * Send a formatted notification
   */
  async sendNotification(
    title: string,
    message: string,
    color: string = 'good'
  ): Promise<IntegrationResponse> {
    return this.sendMessage({
      text: title,
      attachments: [
        {
          color,
          text: message,
        },
      ],
    });
  }
}
