import { SlackIntegration } from '../integrations/slack';
import { SlackConfig, SlackMessage } from '../types';

// Mock @slack/webhook
jest.mock('@slack/webhook');
import { IncomingWebhook } from '@slack/webhook';
const MockedIncomingWebhook = IncomingWebhook as jest.MockedClass<typeof IncomingWebhook>;

describe('SlackIntegration', () => {
  const config: SlackConfig = {
    webhookUrl: 'https://hooks.slack.com/services/TEST/WEBHOOK/URL',
    channel: '#general',
  };

  let slack: SlackIntegration;
  let mockSend: jest.Mock;

  beforeEach(() => {
    mockSend = jest.fn().mockResolvedValue({});
    MockedIncomingWebhook.mockImplementation(() => ({
      send: mockSend,
    } as any));
    
    slack = new SlackIntegration(config);
    jest.clearAllMocks();
  });

  describe('sendMessage', () => {
    it('should send a simple message successfully', async () => {
      const message: SlackMessage = {
        text: 'Hello, World!',
      };

      const result = await slack.sendMessage(message);

      expect(result.success).toBe(true);
      expect(mockSend).toHaveBeenCalledWith(
        expect.objectContaining({
          text: 'Hello, World!',
          channel: '#general',
        })
      );
    });

    it('should send message with custom channel', async () => {
      const message: SlackMessage = {
        text: 'Custom channel message',
        channel: '#alerts',
      };

      await slack.sendMessage(message);

      expect(mockSend).toHaveBeenCalledWith(
        expect.objectContaining({
          text: 'Custom channel message',
          channel: '#alerts',
        })
      );
    });

    it('should send message with username and emoji', async () => {
      const message: SlackMessage = {
        text: 'Bot message',
        username: 'TestBot',
        iconEmoji: ':robot_face:',
      };

      await slack.sendMessage(message);

      expect(mockSend).toHaveBeenCalledWith(
        expect.objectContaining({
          text: 'Bot message',
          username: 'TestBot',
          icon_emoji: ':robot_face:',
        })
      );
    });

    it('should send message with attachments', async () => {
      const message: SlackMessage = {
        text: 'Alert!',
        attachments: [
          {
            color: 'danger',
            title: 'Error Occurred',
            text: 'An error has occurred in the system',
            fields: [
              { title: 'Severity', value: 'High', short: true },
              { title: 'Component', value: 'Database', short: true },
            ],
          },
        ],
      };

      await slack.sendMessage(message);

      expect(mockSend).toHaveBeenCalledWith(
        expect.objectContaining({
          text: 'Alert!',
          attachments: [
            expect.objectContaining({
              color: 'danger',
              title: 'Error Occurred',
              text: 'An error has occurred in the system',
            }),
          ],
        })
      );
    });

    it('should handle errors when sending message', async () => {
      mockSend.mockRejectedValue(new Error('Network error'));

      const message: SlackMessage = {
        text: 'Test message',
      };

      const result = await slack.sendMessage(message);

      expect(result.success).toBe(false);
      expect(result.error).toContain('Network error');
    });
  });

  describe('sendSimpleMessage', () => {
    it('should send a simple text message', async () => {
      const result = await slack.sendSimpleMessage('Quick message');

      expect(result.success).toBe(true);
      expect(mockSend).toHaveBeenCalledWith(
        expect.objectContaining({
          text: 'Quick message',
          channel: '#general',
        })
      );
    });

    it('should send simple message to custom channel', async () => {
      await slack.sendSimpleMessage('Quick message', '#dev');

      expect(mockSend).toHaveBeenCalledWith(
        expect.objectContaining({
          text: 'Quick message',
          channel: '#dev',
        })
      );
    });
  });

  describe('sendNotification', () => {
    it('should send a formatted notification', async () => {
      const result = await slack.sendNotification('Success', 'Operation completed', 'good');

      expect(result.success).toBe(true);
      expect(mockSend).toHaveBeenCalledWith(
        expect.objectContaining({
          text: 'Success',
          attachments: [
            expect.objectContaining({
              color: 'good',
              text: 'Operation completed',
            }),
          ],
        })
      );
    });

    it('should send notification with default color', async () => {
      await slack.sendNotification('Info', 'Information message');

      expect(mockSend).toHaveBeenCalledWith(
        expect.objectContaining({
          attachments: [
            expect.objectContaining({
              color: 'good',
            }),
          ],
        })
      );
    });
  });
});
