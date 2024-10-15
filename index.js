const { Client, GatewayIntentBits, Partials, PermissionsBitField, ActionRowBuilder, ButtonBuilder, ButtonStyle, ModalBuilder, TextInputBuilder, TextInputStyle, EmbedBuilder, Events } = require('discord.js');
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildMembers,
    ],
    partials: [Partials.Channel]
});

const TOKEN = 'MTI5NTUzOTU5NDE0MTUwMzQ4OA.GYz_3C.ZVVxhrlcS35o7BB0wQfbSfH4ASodCRSa_XtyFk';
const VERIFICATION_CHANNEL_IDS = ['1295687991276208229', '1295687991276208230', '1295687991276208231']; // IDs dos canais de verificação
const SENTINELS_ROLE_ID = '';
const PASSWORD = 'fBNZA2zWRrp';

client.once('ready', () => {
    console.log(`Bot está online como ${client.user.tag}`);
});

client.on('messageCreate', async (message) => {
    if (message.content === '!sentinels' && VERIFICATION_CHANNEL_IDS.includes(message.channel.id)) {
        await message.channel.bulkDelete(100);

        const row = new ActionRowBuilder()
            .addComponents(
                new ButtonBuilder()
                    .setCustomId('verifyButton')
                    .setLabel('Verificar')
                    .setStyle(ButtonStyle.Primary)
            );

        const embed = new EmbedBuilder()
            .setColor('#000000')
            .setTitle('Verificação de Sentinels')
            .setDescription('Antes de clicar no botão **verificar,** vá para o canal **<#1294162585716789391>** para ter acesso à senha. 🔒🔑');

        await message.channel.send({
            embeds: [embed],
            components: [row],
        });
    }
});

client.on('interactionCreate', async (interaction) => {
    if (!interaction.isButton()) return;

    if (interaction.customId === 'verifyButton') {
        const modal = new ModalBuilder()
            .setCustomId('passwordModal')
            .setTitle('Verificação de Senha');

        const passwordInput = new TextInputBuilder()
            .setCustomId('passwordInput')
            .setLabel('Digite a senha')
            .setStyle(TextInputStyle.Short)
            .setRequired(true);

        const actionRow = new ActionRowBuilder().addComponents(passwordInput);
        modal.addComponents(actionRow);

        await interaction.showModal(modal);
    }
});

client.on(Events.InteractionCreate, async (interaction) => {
    if (!interaction.isModalSubmit()) return;

    if (interaction.customId === 'passwordModal') {
        const password = interaction.fields.getTextInputValue('passwordInput');

        if (password === PASSWORD) {
            const guild = interaction.guild;
            const member = interaction.member;
            const roleSentinels = guild.roles.cache.get(SENTINELS_ROLE_ID);

            if (roleSentinels) {
                await member.roles.add(roleSentinels);

                const successEmbed = new EmbedBuilder()
                    .setColor('#000000')
                    .setTitle('Verificação Bem-sucedida')
                    .setDescription('Verificação bem-sucedida! Você recebeu o cargo **Sentinels**.');

                await interaction.reply({ embeds: [successEmbed], ephemeral: true });

                const channel = guild.channels.cache.get(interaction.channelId);
                if (channel) {
                    await channel.bulkDelete(100);

                    const row = new ActionRowBuilder()
                        .addComponents(
                            new ButtonBuilder()
                                .setCustomId('verifyButton')
                                .setLabel('Verificar')
                                .setStyle(ButtonStyle.Primary)
                        );

                    const embed = new EmbedBuilder()
                        .setColor('#000000')
                        .setTitle('Verificação da Sentinels')
                        .setDescription('Antes de clicar no botão **verificar,** vá para o canal **<#1294162585716789391>** para ter acesso à senha. 🔒🔑');

                    await channel.send({
                        embeds: [embed],
                        components: [row],
                    });
                }
            }
        } else {
            await interaction.reply({ content: 'Senha incorreta. Tente novamente.', ephemeral: true });
        }
    }
});

client.login(TOKEN);
